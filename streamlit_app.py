import streamlit as st
import pandas as pd
from collections import Counter

def load_data(uploaded_file):
    df = pd.read_excel(uploaded_file)
    df['Permissions'] = df['Permissions'].apply(lambda x: x.split(', '))
    return df

def main():
    st.title('Persona Permissions Management')

    # File uploader
    uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])
    
    if uploaded_file:
        df = load_data(uploaded_file)

        # Calculate statistics
        permission_counts = Counter(permission for permissions in df['Permissions'] for permission in permissions)

        # Statistics section
        st.header('Permission Statistics')
        st.bar_chart(permission_counts)

        # Filter section
        st.header('Filter Personas by Permission')
        permission_list = list(permission_counts.keys())
        selected_permission = st.selectbox('Select a Permission', permission_list)
        filtered_df = df[df['Permissions'].apply(lambda x: selected_permission in x)]
        st.write(filtered_df[['Name', 'Tag', 'Faction']])

        # Edit section
        st.header('Edit Permissions')
        permission_to_replace = st.selectbox('Permission to replace', permission_list)
        new_permission = st.text_input('New Permission')
        if st.button('Replace'):
            df['Permissions'] = df['Permissions'].apply(lambda x: [new_permission if p == permission_to_replace else p for p in x])
            st.success(f'Replaced {permission_to_replace} with {new_permission}')
            # Recalculate statistics after replacement
            permission_counts = Counter(permission for permissions in df['Permissions'] for permission in permissions)
            st.bar_chart(permission_counts)

if __name__ == "__main__":
    main()
