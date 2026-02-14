from typing import List, Dict, Any
from sqlalchemy.orm import Session
from decimal import Decimal

from app.db import models

class EligibilityMatcher:
    """Rule-based eligibility matching engine"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def evaluate_rule(self, user_profile: models.UserProfile, rule: models.EligibilityRule) -> bool:
        """Evaluate a single eligibility rule against user profile"""
        
        # Map rule types to user profile attributes
        profile_value = self._get_profile_value(user_profile, rule.rule_type)
        
        if profile_value is None:
            return not rule.is_mandatory
        
        # Evaluate based on operator
        if rule.operator == ">":
            return profile_value > rule.value_min
        elif rule.operator == "<":
            return profile_value < rule.value_max
        elif rule.operator == ">=":
            return profile_value >= rule.value_min
        elif rule.operator == "<=":
            return profile_value <= rule.value_max
        elif rule.operator == "=":
            return profile_value == rule.value_min
        elif rule.operator == "BETWEEN":
            return rule.value_min <= profile_value <= rule.value_max
        elif rule.operator == "IN":
            return str(profile_value) in rule.value_list
        
        return False
    
    def _get_profile_value(self, profile: models.UserProfile, rule_type: str) -> Any:
        """Extract value from user profile based on rule type"""
        mapping = {
            "age": profile.age,
            "income": profile.annual_income,
            "gender": profile.gender,
            "state": profile.state,
            "district": profile.district,
            "caste": profile.caste_category,
            "occupation": profile.occupation,
            "family_size": profile.family_size,
            "is_bpl": profile.is_bpl,
            "has_disability": profile.has_disability,
            "education": profile.education_level,
            "land_ownership": profile.land_ownership
        }
        return mapping.get(rule_type)
    
    def filter_eligible_schemes(self, user_profile: models.UserProfile) -> List[models.Scheme]:
        """Filter schemes based on eligibility rules"""
        all_schemes = self.db.query(models.Scheme).filter(
            models.Scheme.is_active == True
        ).all()
        
        eligible_schemes = []
        
        for scheme in all_schemes:
            rules = self.db.query(models.EligibilityRule).filter(
                models.EligibilityRule.scheme_id == scheme.id
            ).all()
            
            if not rules:
                # No rules means everyone is eligible
                eligible_schemes.append(scheme)
                continue
            
            # Check all mandatory rules
            mandatory_rules = [r for r in rules if r.is_mandatory]
            if all(self.evaluate_rule(user_profile, rule) for rule in mandatory_rules):
                eligible_schemes.append(scheme)
        
        return eligible_schemes


class SchemeRanker:
    """AI-powered scheme ranking engine"""
    
    def rank_schemes(
        self, 
        user_profile: models.UserProfile, 
        eligible_schemes: List[models.Scheme]
    ) -> List[Dict[str, Any]]:
        """Rank eligible schemes based on relevance"""
        
        ranked = []
        for scheme in eligible_schemes:
            score = self._calculate_score(user_profile, scheme)
            ranked.append({
                "scheme": scheme,
                "score": score
            })
        
        # Sort by score descending
        ranked.sort(key=lambda x: x["score"], reverse=True)
        
        return ranked[:10]  # Top 10
    
    def _calculate_score(self, profile: models.UserProfile, scheme: models.Scheme) -> float:
        """Calculate relevance score for a scheme"""
        score = 0.0
        
        # Benefit amount weight (30%)
        if scheme.benefit_amount:
            score += min(float(scheme.benefit_amount) / 100000, 1.0) * 30
        
        # Location match (25%)
        if scheme.state == profile.state:
            score += 25
        elif scheme.is_central:
            score += 20
        
        # Category relevance (20%)
        if profile.is_bpl and "bpl" in (scheme.category or "").lower():
            score += 20
        if profile.has_disability and "disability" in (scheme.category or "").lower():
            score += 20
        
        # Income-based (15%)
        if profile.annual_income and scheme.benefit_amount:
            income_ratio = float(scheme.benefit_amount) / float(profile.annual_income)
            score += min(income_ratio * 10, 15)
        
        # Recency (10%)
        # Newer schemes get higher scores
        score += 10
        
        return min(score, 100.0)


class RecommendationEngine:
    """Main recommendation engine combining filtering and ranking"""
    
    def __init__(self, db: Session):
        self.db = db
        self.matcher = EligibilityMatcher(db)
        self.ranker = SchemeRanker()
    
    def generate_recommendations(self, user_id: str) -> List[Dict[str, Any]]:
        """Generate personalized scheme recommendations"""
        
        # Get user profile
        user = self.db.query(models.User).filter(models.User.id == user_id).first()
        if not user or not user.profile:
            return []
        
        # Step 1: Filter eligible schemes
        eligible_schemes = self.matcher.filter_eligible_schemes(user.profile)
        
        # Step 2: Rank schemes
        ranked_schemes = self.ranker.rank_schemes(user.profile, eligible_schemes)
        
        return ranked_schemes
