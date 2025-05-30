from typing import Any, Dict, List, Union
from enum import Enum



class WizardState:
    id: str
    type: str
    currentStep: str
    steps: List[WizardStep]
    data: Dict[str, Any>
    isComplete: bool
    createdAt: str
    updatedAt: str
class WizardStep:
    id: str
    title: str
    description?: str
    fields: List[WizardField]
    validations?: Dict[str, WizardValidationRule[]>
    nextStep?: str
    previousStep?: str
    isOptional?: bool
    properties?: Dict[str, Any>
class WizardValidation:
    isValid: bool
    errors: List[ValidationError]
    warnings?: List[ValidationError]
    suggestions?: List[str]
class WizardStepType(Enum):
    FORM = 'FORM'
    SELECTION = 'SELECTION'
    CONFIRMATION = 'CONFIRMATION'
    SUMMARY = 'SUMMARY'
class WizardStepConfig:
    type: \'WizardStepType\'
    validationRules?: Dict[str, Any>
    requiredFields?: List[str]
    customValidation?: (data: Any) => Awaitable[WizardValidation>
    onComplete?: (data: Any) => Awaitable[None>
class WizardValidationRule:
    type: Union['required', 'minLength', 'maxLength', 'pattern', 'custom']
    value?: Any
    message: str
class WizardField:
    id: str
    type: Union['text', 'float', 'select', 'multiselect', 'checkbox', 'radio', 'custom']
    label: str
    placeholder?: str
    defaultValue?: Any
    options?: List[{ value: Any
    label: str>
  validations?: WizardValidationRule[]
  properties?: Record<string, any>
}
class WizardCreateDTO:
    type: str
    steps: List[WizardStep]
    initialData?: Dict[str, Any>
WizardUpdateDTO = Partial[WizardCreateDTO]