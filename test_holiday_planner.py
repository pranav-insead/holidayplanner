#!/usr/bin/env python3
"""
Tests for Holiday Planner
"""
import unittest
import os
import json
from datetime import datetime, timedelta
from holiday_planner import HolidayPlanner


class TestHolidayPlanner(unittest.TestCase):
    """Test cases for the HolidayPlanner class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_file = "test_holidays.json"
        self.planner = HolidayPlanner(data_file=self.test_file)
    
    def tearDown(self):
        """Clean up test files"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
    
    def test_add_holiday(self):
        """Test adding a holiday"""
        holiday = self.planner.add_holiday(
            name="Christmas Vacation",
            start_date="2025-12-20",
            end_date="2025-12-27",
            destination="Swiss Alps",
            notes="Skiing trip"
        )
        
        self.assertEqual(holiday["name"], "Christmas Vacation")
        self.assertEqual(holiday["start_date"], "2025-12-20")
        self.assertEqual(holiday["end_date"], "2025-12-27")
        self.assertEqual(holiday["destination"], "Swiss Alps")
        self.assertEqual(holiday["notes"], "Skiing trip")
        self.assertEqual(len(self.planner.holidays), 1)
    
    def test_add_holiday_invalid_date(self):
        """Test adding a holiday with invalid date format"""
        with self.assertRaises(ValueError):
            self.planner.add_holiday(
                name="Invalid Holiday",
                start_date="20-12-2025",
                end_date="27-12-2025",
                destination="Somewhere",
                notes=""
            )
    
    def test_list_holidays(self):
        """Test listing all holidays"""
        self.planner.add_holiday(
            name="Summer Vacation",
            start_date="2025-07-01",
            end_date="2025-07-15",
            destination="Bali",
            notes="Beach resort"
        )
        self.planner.add_holiday(
            name="Winter Break",
            start_date="2025-12-20",
            end_date="2025-12-27",
            destination="Switzerland",
            notes="Skiing"
        )
        
        holidays = self.planner.list_holidays()
        self.assertEqual(len(holidays), 2)
        self.assertEqual(holidays[0]["name"], "Summer Vacation")
        self.assertEqual(holidays[1]["name"], "Winter Break")
    
    def test_list_upcoming_holidays(self):
        """Test listing only upcoming holidays"""
        # Add a past holiday
        past_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        self.planner.add_holiday(
            name="Past Holiday",
            start_date=past_date,
            end_date=past_date,
            destination="Somewhere",
            notes=""
        )
        
        # Add a future holiday
        future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        self.planner.add_holiday(
            name="Future Holiday",
            start_date=future_date,
            end_date=future_date,
            destination="Somewhere else",
            notes=""
        )
        
        upcoming = self.planner.list_holidays(upcoming_only=True)
        self.assertEqual(len(upcoming), 1)
        self.assertEqual(upcoming[0]["name"], "Future Holiday")
    
    def test_get_holiday(self):
        """Test getting a specific holiday"""
        holiday = self.planner.add_holiday(
            name="Test Holiday",
            start_date="2025-06-01",
            end_date="2025-06-10",
            destination="Test Location",
            notes="Test notes"
        )
        
        retrieved = self.planner.get_holiday(holiday["id"])
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["name"], "Test Holiday")
        
        not_found = self.planner.get_holiday(999)
        self.assertIsNone(not_found)
    
    def test_remove_holiday(self):
        """Test removing a holiday"""
        holiday = self.planner.add_holiday(
            name="To Be Removed",
            start_date="2025-06-01",
            end_date="2025-06-10",
            destination="Test Location",
            notes=""
        )
        
        result = self.planner.remove_holiday(holiday["id"])
        self.assertTrue(result)
        self.assertEqual(len(self.planner.holidays), 0)
        
        result = self.planner.remove_holiday(999)
        self.assertFalse(result)
    
    def test_update_holiday(self):
        """Test updating a holiday"""
        holiday = self.planner.add_holiday(
            name="Original Name",
            start_date="2025-06-01",
            end_date="2025-06-10",
            destination="Original Location",
            notes="Original notes"
        )
        
        updated = self.planner.update_holiday(
            holiday["id"],
            name="Updated Name",
            destination="New Location"
        )
        
        self.assertIsNotNone(updated)
        self.assertEqual(updated["name"], "Updated Name")
        self.assertEqual(updated["destination"], "New Location")
        self.assertEqual(updated["start_date"], "2025-06-01")  # Unchanged
    
    def test_update_holiday_invalid_date(self):
        """Test updating a holiday with invalid date"""
        holiday = self.planner.add_holiday(
            name="Test Holiday",
            start_date="2025-06-01",
            end_date="2025-06-10",
            destination="Test Location",
            notes=""
        )
        
        with self.assertRaises(ValueError):
            self.planner.update_holiday(
                holiday["id"],
                start_date="invalid-date"
            )
    
    def test_update_nonexistent_holiday(self):
        """Test updating a holiday that doesn't exist"""
        result = self.planner.update_holiday(999, name="New Name")
        self.assertIsNone(result)
    
    def test_persistence(self):
        """Test that holidays are persisted to file"""
        self.planner.add_holiday(
            name="Persistent Holiday",
            start_date="2025-08-01",
            end_date="2025-08-10",
            destination="Test Location",
            notes="Test persistence"
        )
        
        # Create a new planner instance with the same file
        new_planner = HolidayPlanner(data_file=self.test_file)
        self.assertEqual(len(new_planner.holidays), 1)
        self.assertEqual(new_planner.holidays[0]["name"], "Persistent Holiday")
    
    def test_empty_planner(self):
        """Test operations on an empty planner"""
        holidays = self.planner.list_holidays()
        self.assertEqual(len(holidays), 0)
        
        upcoming = self.planner.list_holidays(upcoming_only=True)
        self.assertEqual(len(upcoming), 0)
        
        holiday = self.planner.get_holiday(1)
        self.assertIsNone(holiday)


if __name__ == "__main__":
    unittest.main()
