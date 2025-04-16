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
st.write("The name on your Smmothie will be: ", name_on_order)


cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))
#st.dataframe(data=my_dataframe, use_container_width=True)
#st.stop()
pd_df=my_dataframe.to_pandas()
#st.dataframe(pd_df)
#st.stop()
                                                                    
# Correcting the multiselect and syntax issue
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients: '
    , my_dataframe  # Convert Snowflake DataFrame to Pandas for options
    , max_selections = 5
)

if ingredients_list:
  ingredients_string = ''
  
  for fruit_chosen in ingredients_list:
    ingredients_string += fruit_chosen + ''
    
    search_on=pd_df. loc[pd_df ['FRUIT_NAME' ] == fruit_chosen, 'SEARCH_ON'].iloc[0]
    #st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
    
    st.subheader(fruit_chosen + ' Nutrion Information')
    smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)
    sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width = True)
    
    
    my_insert_stmt = """ 
    insert into smoothies.public.orders (ingredients, name_on_order) 
    values ('""" + ingredients_string.strip() + """', '""" + name_on_order + """')
    """
    
    # Primero define la variable
time_to_insert = st.button('Submit Order', key='unique_submit_order_button')

# Luego úsala en la condición
if time_to_insert:
    session.sql(my_insert_stmt).collect()
    st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")
