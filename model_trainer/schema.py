from marshmallow import Schema, fields, validates, ValidationError

class KafkaSettings(Schema):
    name = fields.Str()
    path_to_time = fields.Str()
    path_to_value = fields.Str()
    filterType = fields.Str() 
    filterValue = fields.Str()
    ksql_url = fields.Str()
    timestamp_format = fields.Str()
    time_range_value: float
    time_range_level = fields.Str()

    @validates("filterType")
    def validate_data_source(self, value):
        if value not in ['device_id', 'operator_id', 'import_id']:
            raise ValidationError(f"Filter Type {value} not allowed")

class Job(Schema):
    data_source = fields.Str()
    data_settings = fields.Nested(KafkaSettings)
    toolbox_version = fields.Str()
    ray_image = fields.Str()

    @validates("data_source")
    def validate_data_source(self, value):
        if value not in ['kafka', 's3']:
            raise ValidationError(f"Data Source {value} not allowed")