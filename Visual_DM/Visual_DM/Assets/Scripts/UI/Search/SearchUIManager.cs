using UnityEngine;
using VisualDM.UI.Search;
using System.Collections.Generic;
using System;

namespace VisualDM.UI.Search
{
    public class SearchUIManager : MonoBehaviour
    {
        private SearchInput searchInput;
        private FilterBuilder filterBuilder;
        private SearchResultsDisplay resultsDisplay;
        private EntityResultDisplay entityDisplay;

        void Start()
        {
            // Instantiate all components at runtime
            searchInput = CreateComponent<SearchInput>("SearchInput");
            filterBuilder = CreateComponent<FilterBuilder>("FilterBuilder");
            resultsDisplay = CreateComponent<SearchResultsDisplay>("ResultsDisplay");
            entityDisplay = CreateComponent<EntityResultDisplay>("EntityDisplay");

            // Layout
            searchInput.transform.position = new Vector3(100, 600, 0);
            filterBuilder.transform.position = new Vector3(100, 500, 0);
            resultsDisplay.transform.position = new Vector3(100, 100, 0);
            entityDisplay.transform.position = new Vector3(800, 100, 0);

            // Wire up events
            searchInput.OnSearchSubmitted += OnSearchSubmitted;
            searchInput.OnSuggestionSelected += OnSuggestionSelected;
            filterBuilder.OnFiltersChanged += OnFiltersChanged;
            resultsDisplay.OnPageChanged += OnPageChanged;
            resultsDisplay.OnSortChanged += OnSortChanged;
        }

        private T CreateComponent<T>(string name) where T : Component
        {
            var go = new GameObject(name);
            go.transform.SetParent(transform);
            return go.AddComponent<T>();
        }

        private void OnSearchSubmitted(string query)
        {
            try
            {
                // TODO: Call backend search API with query and filters
                // Update resultsDisplay with new results
            }
            catch (Exception ex)
            {
                VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "Search submission failed.", "SearchUIManager.OnSearchSubmitted");
            }
        }

        private void OnSuggestionSelected(string suggestion)
        {
            try
            {
                // Optionally auto-submit search or update input
            }
            catch (Exception ex)
            {
                VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "Suggestion selection failed.", "SearchUIManager.OnSuggestionSelected");
            }
        }

        private void OnFiltersChanged(List<string> filters)
        {
            try
            {
                // TODO: Call backend search API with current query and filters
            }
            catch (Exception ex)
            {
                VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "Filter change failed.", "SearchUIManager.OnFiltersChanged");
            }
        }

        private void OnPageChanged(int newPage)
        {
            try
            {
                // TODO: Fetch next/prev page from backend
            }
            catch (Exception ex)
            {
                VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "Page change failed.", "SearchUIManager.OnPageChanged");
            }
        }

        private void OnSortChanged(string sortField)
        {
            try
            {
                // TODO: Update search results with new sort order
            }
            catch (Exception ex)
            {
                VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "Sort change failed.", "SearchUIManager.OnSortChanged");
            }
        }
    }
} 