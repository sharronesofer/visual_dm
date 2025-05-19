using System;
using System.Collections.Generic;

namespace VisualDM.World
{
    public class CalendarSystem
    {
        public class ImportantDate
        {
            public string Name;
            public int Year;
            public int Month;
            public int Day;
        }

        private List<ImportantDate> importantDates = new List<ImportantDate>();

        public int DaysPerMonth { get; private set; } = 30;
        public int MonthsPerYear { get; private set; } = 12;
        public bool UseLeapYears { get; private set; } = false;
        public int LeapYearInterval { get; private set; } = 4;

        public void ConfigureCalendar(int daysPerMonth, int monthsPerYear, bool useLeapYears = false, int leapYearInterval = 4)
        {
            DaysPerMonth = daysPerMonth;
            MonthsPerYear = monthsPerYear;
            UseLeapYears = useLeapYears;
            LeapYearInterval = leapYearInterval;
        }

        public bool IsLeapYear(int year) => UseLeapYears && (year % LeapYearInterval == 0);

        public int GetDaysInMonth(int year, int month)
        {
            if (UseLeapYears && month == MonthsPerYear && IsLeapYear(year))
                return DaysPerMonth + 1;
            return DaysPerMonth;
        }

        public void AddImportantDate(string name, int year, int month, int day)
        {
            importantDates.Add(new ImportantDate { Name = name, Year = year, Month = month, Day = day });
        }

        public void RemoveImportantDate(string name)
        {
            importantDates.RemoveAll(d => d.Name == name);
        }

        public IEnumerable<ImportantDate> GetImportantDatesForDay(int year, int month, int day)
        {
            foreach (var date in importantDates)
            {
                if (date.Year == year && date.Month == month && date.Day == day)
                    yield return date;
            }
        }

        public IEnumerable<ImportantDate> GetAllImportantDates() => importantDates;

        // Serialization for save/load
        public CalendarData GetSerializableData() => new CalendarData {
            DaysPerMonth = DaysPerMonth, MonthsPerYear = MonthsPerYear, UseLeapYears = UseLeapYears, LeapYearInterval = LeapYearInterval, ImportantDates = importantDates
        };

        public void LoadFromData(CalendarData data)
        {
            DaysPerMonth = data.DaysPerMonth;
            MonthsPerYear = data.MonthsPerYear;
            UseLeapYears = data.UseLeapYears;
            LeapYearInterval = data.LeapYearInterval;
            importantDates = data.ImportantDates ?? new List<ImportantDate>();
        }

        [Serializable]
        public class CalendarData {
            public int DaysPerMonth, MonthsPerYear, LeapYearInterval;
            public bool UseLeapYears;
            public List<ImportantDate> ImportantDates;
        }
    }
} 