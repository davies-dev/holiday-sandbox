#!/usr/bin/env python3
"""
Test script for rule management functionality in the Study Librarian application.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))
from scripts.db_access import DatabaseAccess
from scripts.config import DB_PARAMS

def test_rule_management():
    """Test the rule management functionality."""
    print("Testing Rule Management Functionality")
    print("=" * 60)
    
    # Initialize database connection
    db = DatabaseAccess(**DB_PARAMS)
    
    try:
        # Test 1: Get existing tags (from previous test)
        print("\n1. Getting existing tags...")
        all_tags = db.get_all_tags()
        print(f"   Found {len(all_tags)} tags:")
        for tag_id, tag_name in all_tags:
            print(f"     ID {tag_id}: {tag_name}")
        
        if not all_tags:
            print("   No tags found. Creating test tags first...")
            test_tags = [
                ("DelayedCBetOOP", "Delayed continuation bet out of position"),
                ("3BetBluff", "Three-bet bluff situations")
            ]
            for tag_name, description in test_tags:
                success = db.create_tag(tag_name, description)
                print(f"   Created tag '{tag_name}': {'✓' if success else '✗'}")
            all_tags = db.get_all_tags()
        
        # Test 2: Create rules for the first tag
        print("\n2. Testing rule creation...")
        if all_tags:
            test_tag_id = all_tags[0][0]  # Use the first tag
            
            # Create test rules
            test_rules = [
                {
                    "tag_id": test_tag_id,
                    "rule_description": "OOP Check/Call, Turn Bet",
                    "pf_pattern": "1f2f3r4r5c6c",
                    "flop_pattern": "1k2k3b4c5c",
                    "turn_pattern": "1b2f3c",
                    "river_pattern": "1b2c"
                },
                {
                    "tag_id": test_tag_id,
                    "rule_description": "IP Bet/Fold on Turn",
                    "pf_pattern": "1f2f3r4r5c6c",
                    "flop_pattern": "1b2c3c",
                    "turn_pattern": "1b2f",
                    "river_pattern": ""
                }
            ]
            
            for rule_data in test_rules:
                success = db.save_rule(rule_data)
                print(f"   Created rule '{rule_data['rule_description']}': {'✓' if success else '✗'}")
        
        # Test 3: Get rules for tag
        print("\n3. Testing get rules for tag...")
        if all_tags:
            test_tag_id = all_tags[0][0]
            rules = db.get_rules_for_tag(test_tag_id)
            print(f"   Found {len(rules)} rules for tag ID {test_tag_id}:")
            for rule_id, desc in rules:
                print(f"     ID {rule_id}: {desc}")
        
        # Test 4: Get rule details
        print("\n4. Testing get rule details...")
        if all_tags:
            test_tag_id = all_tags[0][0]
            rules = db.get_rules_for_tag(test_tag_id)
            if rules:
                test_rule_id = rules[0][0]
                rule_details = db.get_rule_details(test_rule_id)
                if rule_details:
                    print(f"   Rule details for ID {test_rule_id}:")
                    print(f"     Description: {rule_details['rule_description']}")
                    print(f"     Preflop Pattern: {rule_details['pf_pattern']}")
                    print(f"     Flop Pattern: {rule_details['flop_pattern']}")
                    print(f"     Turn Pattern: {rule_details['turn_pattern']}")
                    print(f"     River Pattern: {rule_details['river_pattern']}")
                else:
                    print("   ✗ Could not get rule details")
        
        # Test 5: Update a rule
        print("\n5. Testing rule update...")
        if all_tags:
            test_tag_id = all_tags[0][0]
            rules = db.get_rules_for_tag(test_tag_id)
            if rules:
                test_rule_id = rules[0][0]
                rule_details = db.get_rule_details(test_rule_id)
                if rule_details:
                    # Update the description
                    rule_details['rule_description'] = "Updated: OOP Check/Call, Turn Bet"
                    success = db.save_rule(rule_details)
                    print(f"   Updated rule: {'✓' if success else '✗'}")
                    
                    # Verify the update
                    updated_details = db.get_rule_details(test_rule_id)
                    if updated_details and "Updated:" in updated_details['rule_description']:
                        print("   ✓ Update verified")
                    else:
                        print("   ✗ Update verification failed")
        
        # Test 6: Delete a rule
        print("\n6. Testing rule deletion...")
        if all_tags:
            test_tag_id = all_tags[0][0]
            rules = db.get_rules_for_tag(test_tag_id)
            if len(rules) > 1:  # Only delete if we have more than one rule
                rule_to_delete_id = rules[1][0]  # Delete the second rule
                success = db.delete_rule(rule_to_delete_id)
                print(f"   Deleted rule ID {rule_to_delete_id}: {'✓' if success else '✗'}")
                
                # Verify deletion
                remaining_rules = db.get_rules_for_tag(test_tag_id)
                print(f"   Remaining rules: {len(remaining_rules)}")
            else:
                print("   Skipping deletion test (not enough rules)")
        
        print("\n" + "=" * 60)
        print("Rule management test completed!")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_rule_management() 