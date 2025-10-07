# Holiday Planner

A simple command-line application to plan and manage your holidays throughout the year.

## Features

- **Add holidays**: Create new holiday plans with start/end dates, destinations, and notes
- **List holidays**: View all planned holidays or filter for upcoming ones
- **Update holidays**: Modify existing holiday details
- **Remove holidays**: Delete holidays you no longer need
- **Data persistence**: All holidays are automatically saved to a JSON file

## Installation

1. Clone this repository:
```bash
git clone https://github.com/pranav-insead/holidayplanner.git
cd holidayplanner
```

2. No additional dependencies required - uses only Python standard library!

## Usage

### Run the application

```bash
python3 holiday_planner.py
```

### Interactive Menu

The application provides an interactive menu with the following options:

1. **Add a new holiday** - Enter details for a new holiday plan
2. **List all holidays** - Display all your planned holidays
3. **List upcoming holidays** - Show only future holidays
4. **Remove a holiday** - Delete a holiday by its ID
5. **Update a holiday** - Modify an existing holiday's details
6. **Exit** - Close the application

### Example Usage

```
=== Holiday Planner ===
Welcome to your holiday planning assistant!

Options:
1. Add a new holiday
2. List all holidays
3. List upcoming holidays
4. Remove a holiday
5. Update a holiday
6. Exit

Enter your choice (1-6): 1

--- Add New Holiday ---
Holiday name: Christmas Vacation
Start date (YYYY-MM-DD): 2025-12-20
End date (YYYY-MM-DD): 2025-12-27
Destination: Swiss Alps
Notes (optional): Skiing trip

✓ Holiday added successfully! (ID: 1)
```

## Data Storage

Holidays are stored in `holidays.json` in the same directory. This file is automatically created and updated as you manage your holidays.

## Testing

Run the test suite to verify functionality:

```bash
python3 -m unittest test_holiday_planner.py -v
```

## Date Format

All dates must be entered in **YYYY-MM-DD** format (e.g., 2025-12-25).

## Development

### Project Structure

- `holiday_planner.py` - Main application with CLI and HolidayPlanner class
- `test_holiday_planner.py` - Comprehensive unit tests
- `holidays.json` - Data storage (created automatically)
- `.gitignore` - Git ignore rules

### HolidayPlanner Class

The core functionality is provided by the `HolidayPlanner` class with methods:

- `add_holiday(name, start_date, end_date, destination, notes)` - Add a new holiday
- `list_holidays(upcoming_only)` - List all or upcoming holidays
- `get_holiday(holiday_id)` - Retrieve a specific holiday
- `remove_holiday(holiday_id)` - Delete a holiday
- `update_holiday(holiday_id, **kwargs)` - Update holiday details
- `load_holidays()` - Load from JSON file
- `save_holidays()` - Save to JSON file

## License

This project is open source and available for use.

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests.
