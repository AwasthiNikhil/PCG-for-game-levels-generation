#utils/levelgenerationrules.py

class Rules:
    def __init__(self):
        # "random": 1,
        # "perlin": 2,
        # "simplex": 3,
        # "cellular": 4,
        # "bsp": 5,
        # "graph": 6,
        # "transformer": 7,
        self.level_generation_rules = [
            {'range': range(1, 21), 'method': '1'},
            {'range': range(21, 31), 'method': '7'},
            {'range': range(31, 41), 'method': '4'},
            {'range': range(41, 51), 'method': '6'},
            {'range': range(51, 61), 'method': '2'},
            {'range': range(61, 71), 'method': '1'},
            {'range': range(71, 81), 'method': '6'},
            {'range': range(81, 91), 'method': '4'},
            {'range': range(91, 101), 'method': '7'},
        ]
    def get_generator_for_level(self, level):
        for rule in self.level_generation_rules:
            if level in rule['range']:
                return rule['method']
        return '6'
    def get_seed_for_level(level):
        return hash(f"level_{level}_mygame") % (2**32)
    
 
        
