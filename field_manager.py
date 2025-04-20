import fields



class FieldManager:
    def __init__(self):
        self.field=[]

    def add_field(self,field_type,):
        if field_type=="magnetic":
            field=fields.MagneticField()
