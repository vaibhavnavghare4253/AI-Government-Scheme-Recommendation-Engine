#!/usr/bin/env python3
"""
Seed database with sample schemes for development/testing
"""

import sys
import os
from datetime import date, timedelta

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.db.database import SessionLocal
from app.db import models

def seed_schemes():
    db = SessionLocal()
    
    try:
        # Sample schemes
        schemes_data = [
            {
                "scheme_code": "PM-KISAN",
                "name": "Pradhan Mantri Kisan Samman Nidhi",
                "name_hi": "प्रधानमंत्री किसान सम्मान निधि",
                "description": "Financial support of Rs. 6000 per year to small and marginal farmers",
                "description_hi": "छोटे और सीमांत किसानों को प्रति वर्ष 6000 रुपये की वित्तीय सहायता",
                "department": "Ministry of Agriculture",
                "category": "Agriculture",
                "benefit_type": "Direct Cash Transfer",
                "benefit_amount": 6000,
                "is_central": True,
                "application_url": "https://pmkisan.gov.in",
                "start_date": date(2019, 2, 1),
                "is_active": True
            },
            {
                "scheme_code": "PMAY-G",
                "name": "Pradhan Mantri Awas Yojana - Gramin",
                "name_hi": "प्रधानमंत्री आवास योजना - ग्रामीण",
                "description": "Housing for rural poor with financial assistance up to Rs. 1.2 lakh",
                "description_hi": "ग्रामीण गरीबों के लिए 1.2 लाख रुपये तक की वित्तीय सहायता के साथ आवास",
                "department": "Ministry of Rural Development",
                "category": "Housing",
                "benefit_type": "Financial Assistance",
                "benefit_amount": 120000,
                "is_central": True,
                "application_url": "https://pmayg.nic.in",
                "start_date": date(2016, 11, 20),
                "is_active": True
            },
            {
                "scheme_code": "MGNREGA",
                "name": "Mahatma Gandhi National Rural Employment Guarantee Act",
                "name_hi": "महात्मा गांधी राष्ट्रीय ग्रामीण रोजगार गारंटी अधिनियम",
                "description": "100 days of guaranteed wage employment to rural households",
                "description_hi": "ग्रामीण परिवारों को 100 दिनों की गारंटीकृत मजदूरी रोजगार",
                "department": "Ministry of Rural Development",
                "category": "Employment",
                "benefit_type": "Wage Employment",
                "benefit_amount": 20000,
                "is_central": True,
                "application_url": "https://nrega.nic.in",
                "start_date": date(2006, 2, 2),
                "is_active": True
            },
            {
                "scheme_code": "PMJDY",
                "name": "Pradhan Mantri Jan Dhan Yojana",
                "name_hi": "प्रधानमंत्री जन धन योजना",
                "description": "Financial inclusion program for banking services",
                "description_hi": "बैंकिंग सेवाओं के लिए वित्तीय समावेशन कार्यक्रम",
                "department": "Ministry of Finance",
                "category": "Financial Inclusion",
                "benefit_type": "Banking Services",
                "benefit_amount": 0,
                "is_central": True,
                "application_url": "https://pmjdy.gov.in",
                "start_date": date(2014, 8, 28),
                "is_active": True
            },
            {
                "scheme_code": "NSAP-OAP",
                "name": "National Social Assistance Programme - Old Age Pension",
                "name_hi": "राष्ट्रीय सामाजिक सहायता कार्यक्रम - वृद्धावस्था पेंशन",
                "description": "Monthly pension for elderly citizens below poverty line",
                "description_hi": "गरीबी रेखा से नीचे के बुजुर्ग नागरिकों के लिए मासिक पेंशन",
                "department": "Ministry of Rural Development",
                "category": "Social Security",
                "benefit_type": "Monthly Pension",
                "benefit_amount": 2400,
                "is_central": True,
                "application_url": "https://nsap.nic.in",
                "start_date": date(1995, 8, 15),
                "is_active": True
            }
        ]
        
        print("🌱 Seeding schemes...")
        for scheme_data in schemes_data:
            # Check if scheme already exists
            existing = db.query(models.Scheme).filter(
                models.Scheme.scheme_code == scheme_data["scheme_code"]
            ).first()
            
            if existing:
                print(f"⏭️  Skipping {scheme_data['scheme_code']} (already exists)")
                continue
            
            scheme = models.Scheme(**scheme_data)
            db.add(scheme)
            db.flush()
            
            # Add eligibility rules
            if scheme_data["scheme_code"] == "PM-KISAN":
                rules = [
                    {
                        "scheme_id": scheme.id,
                        "rule_type": "land_ownership",
                        "operator": "<=",
                        "value_max": 2.0,
                        "is_mandatory": True
                    },
                    {
                        "scheme_id": scheme.id,
                        "rule_type": "occupation",
                        "operator": "IN",
                        "value_list": ["Farmer", "Agricultural Worker"],
                        "is_mandatory": True
                    }
                ]
                for rule_data in rules:
                    rule = models.EligibilityRule(**rule_data)
                    db.add(rule)
            
            elif scheme_data["scheme_code"] == "PMAY-G":
                rules = [
                    {
                        "scheme_id": scheme.id,
                        "rule_type": "is_bpl",
                        "operator": "=",
                        "value_min": 1,
                        "is_mandatory": True
                    }
                ]
                for rule_data in rules:
                    rule = models.EligibilityRule(**rule_data)
                    db.add(rule)
            
            elif scheme_data["scheme_code"] == "NSAP-OAP":
                rules = [
                    {
                        "scheme_id": scheme.id,
                        "rule_type": "age",
                        "operator": ">=",
                        "value_min": 60,
                        "is_mandatory": True
                    },
                    {
                        "scheme_id": scheme.id,
                        "rule_type": "is_bpl",
                        "operator": "=",
                        "value_min": 1,
                        "is_mandatory": True
                    }
                ]
                for rule_data in rules:
                    rule = models.EligibilityRule(**rule_data)
                    db.add(rule)
            
            print(f"✅ Added {scheme_data['name']}")
        
        db.commit()
        print("\n🎉 Database seeded successfully!")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_schemes()
