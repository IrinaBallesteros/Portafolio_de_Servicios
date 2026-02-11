def map_columns(df):
    column_map = {}

    for col in df.columns:
        col_lower = col.lower()

        if any(word in col_lower for word in ["nombre", "name", "cliente"]):
            column_map[col] = "name"

        elif any(word in col_lower for word in ["correo", "email", "mail"]):
            column_map[col] = "email"

        elif any(word in col_lower for word in ["id", "cedula", "documento", "dni"]):
            column_map[col] = "id"

        elif any(word in col_lower for word in ["fecha", "date", "nacimiento"]):
            column_map[col] = "birth_date"

        else:
            column_map[col] = col

    return column_map