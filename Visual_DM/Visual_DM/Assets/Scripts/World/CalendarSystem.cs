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
    }
} 