# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col

import requests
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
#st.text(smoothiefroot_response.json())
sf_df = st.dataframe(data=smoothiefroot_responde.json(), use_container_width=true)
# Write directly to the app
st.title(f"Customize Your Smoothie! 🥛")
st.write(
  """Choose the fruits you want in your custom Smoothie!."""
)

name_on_order = st.text_input("Name on Smoothie: ")
st.write("The name on your Smmothie will be: ", name_on_order)


cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
st.dataframe(data=my_dataframe, use_container_width=True)

# Correcting the multiselect and syntax issue
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients: '
    , my_dataframe  # Convert Snowflake DataFrame to Pandas for options
    , max_selections = 5
)

if ingredients_list:
    ingredients_string = ''
    
    # Concatenar todos los ingredientes seleccionados
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
    
    # Construir la sentencia INSERT para incluir tanto ingredientes como nombre del pedido
    my_insert_stmt = """ 
    insert into smoothies.public.orders (ingredients, name_on_order) 
    values ('""" + ingredients_string.strip() + """', '""" + name_on_order + """')
    """
    
    time_to_insert = st.button('Submit Order')
    
    if time_to_insert:
        # Ejecutar el comando SQL sin collect()
        session.sql(my_insert_stmt).collect()
        
        # Agregar el nombre al mensaje de éxito
        st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")

