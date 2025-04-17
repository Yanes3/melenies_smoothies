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
try:
    cnx = st.connection("snowflake")
    session = cnx.session()
    my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
    # Convert Snowflake DataFrame to Pandas DataFrame
    pd_df = my_dataframe.to_pandas()
except Exception as e:
    st.error(f"Could not connect to Snowflake: {str(e)}")
    st.stop()

# Correcting the multiselect and syntax issue
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients: ',
    pd_df['FRUIT_NAME'].tolist(),  # Use Pandas DataFrame for multiselect options
    max_selections=5
)

if ingredients_list:
    ingredients_string = ', '.join(ingredients_list)  # Use join for efficient string concatenation

    for fruit_chosen in ingredients_list:
        try:
            # Get the corresponding SEARCH_ON value for the selected fruit
            search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]

            # Fetch nutrition information for the selected fruit from the API
            smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
            smoothiefroot_response.raise_for_status()  # Raise an error if the request fails

            st.subheader(f'{fruit_chosen} Nutrition Information')
            st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
        except Exception as api_error:
            st.error(f"Error fetching data for {fruit_chosen}: {str(api_error)}")

    # Build the INSERT statement for the smoothie order
    my_insert_stmt = """
    INSERT INTO smoothies.public.orders (ingredients, name_on_order)
    VALUES (%s, %s)
    """
    
    # Button to submit the order
    time_to_insert = st.button('Submit Order', key='unique_submit_order_button')

    # Insert the order when the button is clicked
    if time_to_insert:
        try:
            session.sql(my_insert_stmt, (ingredients_string, name_on_order)).collect()  # Use parameterized query
            st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")
        except Exception as db_error:
            st.error(f"Could not submit order: {str(db_error)}")
