from processors.layer_1_rules import Layer1Rules
from processors.layer_2_ai import Layer2AI

class NormaDBEngine:
    def __init__(self, use_layer1=True, use_layer2=False):
        # Aquí definimos qué módulos se activan según el contrato/paquete
        self.pipeline = []
        if use_layer1: self.pipeline.append(Layer1Rules())
        if use_layer2: self.pipeline.append(Layer2AI())

    def run(self, df):
        for processor in self.pipeline:
            df = processor.process(df)
        return df