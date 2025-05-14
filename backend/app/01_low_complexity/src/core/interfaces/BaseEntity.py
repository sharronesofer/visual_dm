from typing import Any, Union



class BaseEntity:
    id: Union[str, float]
    createdAt?: Date
    updatedAt?: Date 