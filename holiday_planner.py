#!/usr/bin/env python3
"""
Holiday Planner - A simple application to plan and manage holidays
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Optional


class HolidayPlanner:
    """Main class for managing holidays"""
    
    def __init__(self, data_file: str = "holidays.json"):
        """Initialize the holiday planner with a data file"""
        self.data_file = data_file
        self.holidays: List[Dict] = []
        self.load_holidays()
    
    def load_holidays(self) -> None:
        """Load holidays from the JSON data file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    self.holidays = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading holidays: {e}")
                self.holidays = []
        else:
            self.holidays = []
    
    def save_holidays(self) -> None:
        """Save holidays to the JSON data file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.holidays, f, indent=2)
        except IOError as e:
            print(f"Error saving holidays: {e}")
    
    def add_holiday(self, name: str, start_date: str, end_date: str, 
                    destination: str, notes: str = "") -> Dict:
        """Add a new holiday to the planner"""
        # Validate dates
        try:
            datetime.strptime(start_date, "%Y-%m-%d")
            datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Dates must be in YYYY-MM-DD format")
        
        holiday = {
            "id": len(self.holidays) + 1,
            "name": name,
            "start_date": start_date,
            "end_date": end_date,
            "destination": destination,
            "notes": notes,
            "created_at": datetime.now().isoformat()
        }
        
        self.holidays.append(holiday)
        self.save_holidays()
        return holiday
    
    def list_holidays(self, upcoming_only: bool = False) -> List[Dict]:
        """List all holidays or only upcoming ones"""
        if not upcoming_only:
            return self.holidays
        
        today = datetime.now().date()
        upcoming = []
        for holiday in self.holidays:
            holiday_date = datetime.strptime(holiday["start_date"], "%Y-%m-%d").date()
            if holiday_date >= today:
                upcoming.append(holiday)
        return upcoming
    
    def get_holiday(self, holiday_id: int) -> Optional[Dict]:
        """Get a specific holiday by ID"""
        for holiday in self.holidays:
            if holiday["id"] == holiday_id:
                return holiday
        return None
    
    def remove_holiday(self, holiday_id: int) -> bool:
        """Remove a holiday by ID"""
        for i, holiday in enumerate(self.holidays):
            if holiday["id"] == holiday_id:
                self.holidays.pop(i)
                self.save_holidays()
                return True
        return False
    
    def update_holiday(self, holiday_id: int, **kwargs) -> Optional[Dict]:
        """Update a holiday's details"""
        holiday = self.get_holiday(holiday_id)
        if not holiday:
            return None
        
        # Validate dates if provided
        if "start_date" in kwargs:
            try:
                datetime.strptime(kwargs["start_date"], "%Y-%m-%d")
            except ValueError:
                raise ValueError("Start date must be in YYYY-MM-DD format")
        
        if "end_date" in kwargs:
            try:
                datetime.strptime(kwargs["end_date"], "%Y-%m-%d")
            except ValueError:
                raise ValueError("End date must be in YYYY-MM-DD format")
        
        # Update fields
        for key, value in kwargs.items():
            if key in holiday and key != "id" and key != "created_at":
                holiday[key] = value
        
        self.save_holidays()
        return holiday


def main():
    """Main CLI interface for the holiday planner"""
    planner = HolidayPlanner()
    
    print("\n=== Holiday Planner ===")
    print("Welcome to your holiday planning assistant!")
    
    while True:
        print("\nOptions:")
        print("1. Add a new holiday")
        print("2. List all holidays")
        print("3. List upcoming holidays")
        print("4. Remove a holiday")
        print("5. Update a holiday")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == "1":
            print("\n--- Add New Holiday ---")
            name = input("Holiday name: ").strip()
            start_date = input("Start date (YYYY-MM-DD): ").strip()
            end_date = input("End date (YYYY-MM-DD): ").strip()
            destination = input("Destination: ").strip()
            notes = input("Notes (optional): ").strip()
            
            try:
                holiday = planner.add_holiday(name, start_date, end_date, destination, notes)
                print(f"\n✓ Holiday added successfully! (ID: {holiday['id']})")
            except ValueError as e:
                print(f"\n✗ Error: {e}")
        
        elif choice == "2":
            print("\n--- All Holidays ---")
            holidays = planner.list_holidays()
            if not holidays:
                print("No holidays planned yet.")
            else:
                for h in holidays:
                    print(f"\nID: {h['id']}")
                    print(f"Name: {h['name']}")
                    print(f"Dates: {h['start_date']} to {h['end_date']}")
                    print(f"Destination: {h['destination']}")
                    if h['notes']:
                        print(f"Notes: {h['notes']}")
        
        elif choice == "3":
            print("\n--- Upcoming Holidays ---")
            holidays = planner.list_holidays(upcoming_only=True)
            if not holidays:
                print("No upcoming holidays.")
            else:
                for h in holidays:
                    print(f"\nID: {h['id']}")
                    print(f"Name: {h['name']}")
                    print(f"Dates: {h['start_date']} to {h['end_date']}")
                    print(f"Destination: {h['destination']}")
                    if h['notes']:
                        print(f"Notes: {h['notes']}")
        
        elif choice == "4":
            print("\n--- Remove Holiday ---")
            try:
                holiday_id = int(input("Enter holiday ID to remove: ").strip())
                if planner.remove_holiday(holiday_id):
                    print(f"\n✓ Holiday {holiday_id} removed successfully!")
                else:
                    print(f"\n✗ Holiday {holiday_id} not found.")
            except ValueError:
                print("\n✗ Invalid ID. Please enter a number.")
        
        elif choice == "5":
            print("\n--- Update Holiday ---")
            try:
                holiday_id = int(input("Enter holiday ID to update: ").strip())
                holiday = planner.get_holiday(holiday_id)
                if not holiday:
                    print(f"\n✗ Holiday {holiday_id} not found.")
                    continue
                
                print(f"\nCurrent details for '{holiday['name']}':")
                print(f"Start date: {holiday['start_date']}")
                print(f"End date: {holiday['end_date']}")
                print(f"Destination: {holiday['destination']}")
                print(f"Notes: {holiday['notes']}")
                
                print("\nEnter new values (press Enter to keep current):")
                name = input(f"Name [{holiday['name']}]: ").strip()
                start_date = input(f"Start date [{holiday['start_date']}]: ").strip()
                end_date = input(f"End date [{holiday['end_date']}]: ").strip()
                destination = input(f"Destination [{holiday['destination']}]: ").strip()
                notes = input(f"Notes [{holiday['notes']}]: ").strip()
                
                updates = {}
                if name:
                    updates["name"] = name
                if start_date:
                    updates["start_date"] = start_date
                if end_date:
                    updates["end_date"] = end_date
                if destination:
                    updates["destination"] = destination
                if notes:
                    updates["notes"] = notes
                
                if updates:
                    planner.update_holiday(holiday_id, **updates)
                    print(f"\n✓ Holiday {holiday_id} updated successfully!")
                else:
                    print("\nNo changes made.")
            except ValueError as e:
                print(f"\n✗ Error: {e}")
        
        elif choice == "6":
            print("\nThank you for using Holiday Planner. Goodbye!")
            break
        
        else:
            print("\n✗ Invalid choice. Please enter 1-6.")


if __name__ == "__main__":
    main()
