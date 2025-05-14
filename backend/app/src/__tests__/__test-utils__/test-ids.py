from typing import Any, Dict


const commonTestIds = {
  button: Dict[str, Any],
  input: Dict[str, Any],
  form: Dict[str, Any],
  modal: Dict[str, Any],
  navigation: Dict[str, Any],
  loading: Dict[str, Any],
  error: Dict[str, Any],
}
const featureTestIds = {
  auth: Dict[str, Any],
  profile: Dict[str, Any],
  dashboard: Dict[str, Any],
  settings: Dict[str, Any],
}
const generateTestId = (base: str, identifier: str | number) =>
  `${base}-${identifier}`
const getListItemTestId = (index: float) =>
  generateTestId('list-item', index)
const getTableCellTestId = (row: float, col: float) =>
  `table-cell-${row}-${col}`
const getFormFieldTestId = (fieldName: str) =>
  `form-field-${fieldName}`
const getErrorMessageTestId = (fieldName: str) =>
  `error-message-${fieldName}`
const getModalTestId = (modalName: str) => `modal-${modalName}`
const getButtonTestId = (buttonName: str) => `button-${buttonName}`
const getInputTestId = (inputName: str) => `input-${inputName}`
const getSectionTestId = (sectionName: str) =>
  `section-${sectionName}`
const getTabTestId = (tabName: str) => `tab-${tabName}`
const getPanelTestId = (panelName: str) => `panel-${panelName}`