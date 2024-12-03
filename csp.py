import pandas as pd
from tqdm import tqdm
import pickle
import os

file_name = "data/ddinter_total.csv"
filter_name = "data/filtered_data.csv"
dictionary_file = "data/constraint_data"

levels = {
    "Minor": 1,
    "Moderate": 0.5,
    "Major": 0
}

class CSP:
    def __init__(self, data, prescriptions) -> None:
        self.constraints = {}
        self.data = data
        self.prescriptions = prescriptions
        self.symptoms = list(self.prescriptions.keys())
        self.solution = {}
        self.solution_drugs = []
        self.maximum_weight = 0
        self.best_solution = {}
        self.found_solution = False
        self.bad_constraints = set()

        if os.path.exists(dictionary_file):
            with open(dictionary_file, "rb") as file:
                print("Data Exists -- loading dictionary")
                self.constraints = pickle.load(file)
        else:
            self.find_constraints()
            with open(dictionary_file, "wb") as file:
                print("Dumping dictionary data for later use")
                pickle.dump(self.constraints, file)


    def find_constraints(self) -> None:
        for _, r in tqdm(self.data.iterrows(), total=len(self.data), desc="Building Constraint Dictionary"):
            constraint = (r["Drug_A"], r["Drug_B"])
            opposite = (r["Drug_B"], r["Drug_A"])
            type_weight = r["Level"]
            weight = levels[type_weight]
            self.constraints[constraint] = weight
            self.constraints[opposite] = weight

    def is_safe(self, drug, weight) -> None:
        for k in self.solution.keys():
            found = (self.solution[k], drug)
            found_reverse = (drug, self.solution[k])
            if found in self.constraints and self.constraints[found] == 0:
                if found not in self.bad_constraints and found_reverse not in self.bad_constraints:
                    self.bad_constraints.add(found)
                return False, 0
            if found in self.constraints:
                weight *= self.constraints[found] 
        return True, weight

    def backtracking(self, weight, i=0) -> None:
        if i == len(self.prescriptions):
            if weight > self.maximum_weight:
                self.maximum_weight = weight
                self.best_solution = dict(self.solution)
                self.found_solution = True
            return
        
        symptom = self.symptoms[i]

        if len(self.prescriptions[symptom]) == 0:
            self.solution[symptom] = ""
            self.backtracking(weight, i + 1)
            del self.solution[symptom]

        for drug in self.prescriptions[symptom]:
            safe, new_weight = self.is_safe(drug, weight)
            if safe:
                self.solution[symptom] = drug
                self.backtracking(new_weight, i + 1)
                del self.solution[symptom]
    
    def print_weight(self) -> None:
        weight = 1
        for i in range(len(self.solution_drugs)):
            for j in range(i + 1, len(self.solution_drugs)):
                ddi = (self.solution_drugs[i], self.solution_drugs[j])
                if ddi in self.constraints:
                    constraint = self.constraints[ddi]
                    weight *= constraint

                    print(f"Constraint {ddi}: {constraint}")
                else:
                    print(f"No constraint for {ddi}")

        print(f"Found weight for solution: {weight}")
    
    def find_solution(self) -> None:
        self.backtracking(weight=1)
        self.solution_drugs.clear()
        if self.found_solution:
            print("Solution:")
            for k in self.best_solution.keys():
                print(f"{k}: {self.best_solution[k]}")
                self.solution_drugs.append(self.best_solution[k])
            self.print_weight()
        else:
            print("Solution not found for CSP!")
        if len(self.bad_constraints) != 0:
            print("Major Constraints found:")
            for bad in self.bad_constraints:
                print(f"\t{bad}")


if __name__ == "__main__":
    data = pd.read_csv(file_name)
    filtered_data = data[data["Level"].notna() & (data["Level"] != "Unknown")]
    filtered_data.to_csv(filter_name, index=False)
    data = pd.read_csv(filter_name)

    csp = CSP(data, 
        {
            "Chest Pain": ["Aspirin", "Ibuprofen", "Codeine"],
            "Infections": ["Amoxicillin", "Ciprofloxacin", "Azithromycin"],
            "Joint Swelling": ["Hydroxychloroquine", "Methotrexate", "Prednisolone"],
            "High Blood Sugar": ["Metformin"],
            "High Blood Pressure": ["Losartan", "Furosemide"],
            "Blood Clots": ["Warfarin", "Aspirin"],
            "High Cholesterol": ["Atorvastatin"],
            "Heartburn": ["Omeprazole"],
            # "Thyroid Disorders": ["Levothyroxine"],
            "Fever": ["Paracetamol", "Ibuprofen"]


            # "Common Cold": ['Acetaminophen', 'Acetylsalicylic acid', 'Ammonium chloride', 'Ascorbic acid', 'Bromhexine', 'Brompheniramine', 'Caffeine', 'Camphor', 'Chlorcyclizine', 'Chlorpheniramine', 'Choline salicylate', 'Clemastine', 'Codeine', 'DL-Methylephedrine', 'Desloratadine', 'Dexchlorpheniramine', 'Dexchlorpheniramine maleate', 'Dextromethorphan', 'Diclofenac', 'Dimetindene', 'Diphenhydramine', 'Doxylamine', 'Ephedrine', 'Ethyl nitrite', 'Ethylmorphine', 'Eucalyptus oil', 'Guaifenesin', 'Ibuprofen', 'Isopropamide', 'Levocetirizine', 'Levomenthol', 'Loratadine', 'Mepyramine', 'Noscapine', 'Pelargonium sidoides root', 'Pentoxyverine', 'Pheniramine', 'Phenylephrine', 'Phenylpropanolamine', 'Promethazine', 'Pseudoephedrine', 'Pyridoxine', 'Sodium ascorbate', 'Sodium citrate', 'Terpineol', 'Triprolidine', 'Zinc'],
            # "Asthma": ['Albuterol', 'Ambrosia artemisiifolia pollen', 'Aminophylline', 'Arformoterol', 'Beclomethasone dipropionate', 'Budesonide', 'Carmoterol', 'Chlorpheniramine', 'Ciclesonide', 'Cortisone acetate', 'Cromoglicic acid', 'Desloratadine', 'Dexamethasone', 'Epinephrine', 'Etafedrine', 'Flunisolide', 'Fluticasone', 'Fluticasone furoate', 'Fluticasone propionate', 'Formoterol', 'Guaifenesin', 'Hydrocortisone', 'Indacaterol', 'Ipratropium', 'Lactose', 'Methacholine', 'Methoxyphenamine', 'Methylprednisolone', 'Mometasone', 'Mometasone furoate', 'Mometasone furoate', 'Montelukast', 'Nedocromil', 'Orciprenaline', 'Oxtriphylline', 'Pranlukast', 'Prednisone', 'Racepinephrine', 'Reproterol', 'Salmeterol', 'Sodium citrate', 'Terbutaline', 'Theophylline', 'Tiotropium', 'Triamcinolone', 'Umeclidinium', 'Vilanterol', 'Zafirlukast', 'Zileuton'],
            # "Heartburn": ['Alginic acid', 'Almasilate', 'Aluminium glycinate', 'Aluminum hydroxide', 'Alverine', 'Belladonna', 'Bismuth subsalicylate', 'Calcium carbonate', 'Cimetidine', 'Citric acid', 'Dexlansoprazole', 'Dihydroxyaluminum sodium carbonate', 'Esomeprazole', 'Famotidine', 'Hydrotalcite', 'L-tartaric acid', 'Magaldrate', 'Magnesium carbonate', 'Magnesium hydroxide', 'Magnesium oxide', 'Magnesium trisilicate', 'Omeprazole', 'Pantoprazole', 'Rabeprazole', 'Ranitidine', 'Silodrate', 'Simethicone', 'Sodium bicarbonate', 'Sodium citrate', 'Vonoprazan']
        }
    )
    # if ("Paracetamol","Levothyroxine") in csp.constraints:
    #     print(csp.constraints[("Paracetamol","Levothyroxine")])
    # else:
    #     print("No constraint checking the constraints!")
    csp.find_solution()