# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title(f"Customize Your Smoothie! 🥛")
st.write(
  """Choose the fruits you want in your custom Smoothie!."""
)

name_on_order = st.text_input("Name on Smoothie: ")
st.write("The name on your Smoothie will be: ", name_on_order)

# Conectar a Snowflake
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

# Convertir Snowflake DataFrame a Pandas DataFrame y extraer la columna 'FRUIT_NAME'
fruit_names = my_dataframe.to_pandas()['FRUIT_NAME'].tolist()

# Usar la lista de frutas para el multiselect
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients: ',
    fruit_names,  # Usar la lista de frutas convertida
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ', '  # Corrected for proper ingredient string formatting
        st.subheader(fruit_chosen + ' Nutrition Information')
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{fruit_chosen}")
        st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
    
    # Create the insert statement only once after all ingredients have been selected
    my_insert_stmt = f"""
    insert into smoothies.public.orders (ingredients, name_on_order) 
    values ('{ingredients_string.strip(', ')}', '{name_on_order}')
    """

    # Now place the button outside the loop
    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")
