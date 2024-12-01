# MediCSP

# Sample Command

    python med_solver.py DBCOND0000353 DBCOND0115953 DBCOND0013565 DBCOND0037418 -d Chrome

DBCOND0000353: Common Cold

DBCOND0013565: Asthma

DBCOND0037418: Inflammatory Pain

Alternatively you can construct a CSP object as such:

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
            "Fever": ["Paracetamol", "Ibuprofen"]
        }
    )

    csp.find_solution()