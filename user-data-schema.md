each TypeOfService has a user_data_schema which will render additional fields on the createNumber for that ToS
These can be strings, ints, bool or choice options, 
The data will be stored as a JSON object against the number and availble to the API

{
    "ringbackTone": {
        "type": "str",
        "required": false,
        "label": "Ringback Tone",
        "max_length": 100
    },
    "priority": {
        "type": "int",
        "required": true,
        "label": "Priority Level"
    },
    "enabled": {
        "type": "bool",
        "required": false,
        "label": "Enable Feature"
    },
    "category": {
        "type": "choice",
        "choices": ["Standard", "Premium", "Enterprise"],
        "required": true,
        "label": "Service Category"
    }
}