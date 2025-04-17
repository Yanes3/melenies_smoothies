# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title(f"Customize Your Smoothie! 🥛")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input("Name on Smoothie: ")
st.write("The name on your Smoothie will be: ", name_on_order)

# Establish Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Convert Snowflake DataFrame to Pandas DataFrame
pd_df = my_dataframe.to_pandas()

# Correcting the multiselect and syntax issue
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients: '
    , my_dataframe['FRUIT_NAME'].tolist()  # Convert Snowflake DataFrame to list for multiselect options
    , max_selections=5
)

if ingredients_list:
    ingredients_string = ''
    
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ', '  # Concatenate with a comma for better formatting
        
        # Get the corresponding SEARCH_ON value for the selected fruit
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        
        # Fetch nutrition information for the selected fruit from the API
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
        
        if smoothiefroot_response.status_code == 200:
            st.subheader(f'{fruit_chosen} Nutrition Information')
            st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
        else:
            st.error(f"Error fetching data for {fruit_chosen}")
    
    # Build the INSERT statement for the smoothie order
    my_insert_stmt = f"""
    INSERT INTO smoothies.public.orders (ingredients, name_on_order)
    VALUES ('{ingredients_string.strip(', ')}', '{name_on_order}')
    """

    # Button to submit the order
    time_to_insert = st.button('Submit Order', key='unique_submit_order_button')

    # Insert the order when the button is clicked
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")
