
from __future__ import annotations

import math

modeling_elements_names = {
                    "מדד לוגיסטי אמסל\"ח אישי": "",
                    "מדד לוגיסטי אמסל\"ח מסגרתי": "",
                    "מדד מאג": "",
                    "מדד ציוד רפואי": "",
                    "מדד מב\"ט בסיסי": "",
                    "מדד מב\"ט מתקדם": "",
                    "מדד לוגיסטי צח\"י": "",
                    "מדד לוגיסטי חמ\"ל": "",
                    "מדד לוגיסטי מ\"ה": "",
                    "מדד איוש מ\"ה": "",
                    "מדד ציוד תקשוב מ\"ה": "",
                    "מדד צח\"י": "",
                    "מדד נץ": "",
                    "מדד ציוד לוגיסטי מ\"ה": ""
                    }

modeling_elements_enemy = {"כמות אוייב":"",
                           "מדד כשירות אוייב":"",
                           "מדד אמצעים אוייב":"",
                           "מדד אמל\"ח אוייב":"",
                           "רגלי":"",
                           "רכוב":"",
                           "תת קרקע":"",
                           "אווירי":"",
                           "נשק שובר שיווין":"",
                           "":""}

class StochasticModeling:
    def __init__(
        self,
        criteria_list: dict[str, list[float] | tuple[float, float]],
        settlements_count: int = 1,
    ):
        """
        Build a stochastic model from criteria values.

        Expected input format:
            {
                "<criterion name>": [weight, probability],
                ...
            }

        - weight: numeric non-negative value.
        - probability: numeric value in [0, 1] or [0, 100] (percentage).
        """
        if settlements_count < 1:
            raise ValueError("settlements_count must be >= 1")

        self.settlements_count = int(settlements_count)
        self.criteria_list = self._validate_and_prepare(criteria_list)
        total_weight = sum(item["weight"] for item in self.criteria_list.values())
        self.criteria_normal_weights = {
            criterion: (values["weight"] / total_weight if total_weight else 0.0)
            for criterion, values in self.criteria_list.items()
        }

        self.modeling_elements = {
                    "warfare": ["מדד לוגיסטי אמסל\"ח אישי","מדד איוש מ\"ה" ],
                    "logistic": ["מדד לוגיסטי אמסל\"ח מסגרתי","מדד מאג", "מדד ציוד לוגיסטי מ\"ה", "מדד ציוד תקשוב מ\"ה", "מדד לוגיסטי מ\"ה"],
                    "medical": ["מדד ציוד רפואי"],
                    "defence": ["מדד מב\"ט בסיסי", "מדד מב\"ט מתקדם"],
                    "operations":["מדד לוגיסטי חמ\"ל","מדד נץ"],
                    "urgency_support_group":["מדד צח\"י", "מדד לוגיסטי צח\"י"]
                }

        self.enemy_elements = {
            "warfare": ["מדד אמסל\"ח אישי תוקפים","מדד איוש תוקפים" ],
            "logistic": ["מדד נשק שובר שיוויון תוקפים","מדד אמל\"ח תוקפים", "מדד ציוד לוגיסטי תוקפים", "מדד ציוד קשר תוקפים"],
            "medical": ["מדד ציוד רפואי"],
            "attack": ["מדד מב\"ט בסיסי", "מדד מב\"ט מתקדם"],
            "operations":["מדד לוגיסטי חמ\"ל","מדד נץ"],
            "urgency_support_group":["מדד צח\"י", "מדד לוגיסטי צח\"י"]}

    @staticmethod
    def _normalize_probability(probability: float | str) -> float:
        if isinstance(probability, str):
            probability = probability.strip().replace("%", "")
        probability = float(probability)
        if 0 <= probability <= 1:
            return probability
        if 0 <= probability <= 100:
            return probability / 100.0
        raise ValueError(f"Probability must be in [0, 1] or [0, 100], got {probability}")

    @classmethod
    def _validate_and_prepare(
        cls,
        criteria_list: dict[str, list[float] | tuple[float, float]],
    ) -> dict[str, dict[str, float]]:
        if not isinstance(criteria_list, dict):
            raise TypeError("criteria_list must be a dictionary")

        unknown_keys = [key for key in criteria_list if key not in modeling_elements_names]
        if unknown_keys:
            raise ValueError(f"Unknown modeling keys: {unknown_keys}")

        prepared: dict[str, dict[str, float]] = {}

        for criterion_name in modeling_elements_names.keys():
            raw_pair = criteria_list.get(criterion_name, [0.0, 0.0])

            if not isinstance(raw_pair, (list, tuple)) or len(raw_pair) != 2:
                raise ValueError(
                    f"Criterion '{criterion_name}' must have [weight, probability], got: {raw_pair}"
                )

            weight, probability = raw_pair
            weight = float(weight)
            if weight < 0:
                raise ValueError(f"Weight must be non-negative for '{criterion_name}', got: {weight}")

            prepared[criterion_name] = {
                "weight": weight,
                "probability": cls._normalize_probability(float(probability)),
            }

        return prepared

    def calculate_overhead(self) -> float:
        """
        Compute model overhead as weighted uncertainty.

        overhead = sum(weight * (1 - probability)) / sum(weight)
        Returns a normalized value in [0, 1] (0 means no overhead).
        """
        total_weight = sum(item["weight"] for item in self.criteria_list.values())
        if total_weight == 0:
            return 0.0

        weighted_uncertainty = sum(
            item["weight"] * (1.0 - item["probability"])
            for item in self.criteria_list.values()
        )
        return weighted_uncertainty / total_weight

    def calculate_sampling_overhead(self) -> float:
        """
        Compute adjusted overhead for averaged input over multiple settlements.

        The input is an average across settlements, so uncertainty of the mean
        decreases by sqrt(n). This returns:
            calculate_overhead() / sqrt(settlements_count)
        """
        base_overhead = self.calculate_overhead()
        return base_overhead / math.sqrt(self.settlements_count)

    def _calculate_domain_scores(self) -> dict[str, float]:
        """Calculate weighted expected score per domain (0-100 scale)."""
        domain_scores: dict[str, float] = {}

        for domain_name, criteria_names in self.modeling_elements.items():
            relevant = [self.criteria_list[name] for name in criteria_names if name in self.criteria_list]
            total_weight = sum(item["weight"] for item in relevant)

            if total_weight == 0:
                domain_scores[domain_name] = 0.0
                continue

            weighted_score = sum(item["weight"] * item["probability"] for item in relevant)
            domain_scores[domain_name] = (weighted_score / total_weight) * 100.0

        return domain_scores


    def resolve(self):
        """
        Solve the stochastic model and return a full analysis payload.

        Returns:
            {
                "overall_score": <0-100>,
                "overhead": <0-1>,
                "base_overhead": <0-1>,
                "settlements_count": <int>,
                "domain_scores": { ... },
                "criteria_normal_weights": { ... }
            }
        """
        total_weight = sum(item["weight"] for item in self.criteria_list.values())
        overall_score = 0.0

        if total_weight > 0:
            weighted_success = sum(
                item["weight"] * item["probability"]
                for item in self.criteria_list.values()
            )
            overall_score = (weighted_success / total_weight) * 100.0

        base_overhead = self.calculate_overhead()
        return {
            "overall_score": overall_score,
            "overhead": self.calculate_sampling_overhead(),
            "base_overhead": base_overhead,
            "settlements_count": self.settlements_count,
            "domain_scores": self._calculate_domain_scores(),
            "criteria_normal_weights": self.criteria_normal_weights,
        }








def get_settelmet_data(settlement_name):
    return {"name": settlement_name, "distance": 0}
#############################################################
def status_modeling(settlement_name):
    settlement_data = get_settelmet_data(settlement_name)
    _ = settlement_data

    empty_model_input = {key: [0.0, 0.0] for key in modeling_elements_names.keys()}
    return StochasticModeling(empty_model_input).resolve()


