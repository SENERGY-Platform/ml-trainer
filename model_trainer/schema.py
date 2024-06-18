from marshmallow import Schema, fields, validates, ValidationError

class KafkaSettings(Schema):
    name = fields.Str()
    path_to_time = fields.Str()
    path_to_value = fields.Str()
    filterType = fields.Str() 
    filterValue = fields.Str()
    ksql_url = fields.Str()
    timestamp_format = fields.Str()
    time_range_value = fields.Float()
    time_range_level = fields.Str()

    @validates("filterType")
    def validate_data_source(self, value):
        if value not in ['device_id', 'operator_id', 'import_id']:
            raise ValidationError(f"Filter Type {value} not allowed")

class MlFitSettings(Schema):
    model_name = fields.Str()
    model_parameter = fields.Raw()

    @validates("model_name")
    def validate_model_name(self, value):
        if value not in ['cnn', 'trf']:
            raise ValidationError(f"Model {value} not allowed")

class JobAPI(Schema):
    data_source = fields.Str()
    data_settings = fields.Nested(KafkaSettings)
    toolbox_version = fields.Str()
    ray_image = fields.Str()
    user_id = fields.Str()
    experiment_name = fields.Str()

    @validates("data_source")
    def validate_data_source(self, value):
        if value not in ['kafka', 's3', 'dummy']:
            raise ValidationError(f"Data Source {value} not allowed")


# TODO API Schema, Toolbox Schema?

class RayJobConfig(JobAPI):
    task = fields.Str()

    @validates("task")
    def validate_task(self, value):
        if value not in ['anomaly_detection', 'peak_shaving', 'load_shifting']:
            raise ValidationError(f"ML Use Case {value} not allowed")