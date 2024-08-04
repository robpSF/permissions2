import streamlit as st
import pandas as pd
from collections import Counter

def load_data(uploaded_file):
    df = pd.read_excel(uploaded_file)
    df['Permissions'] = df['Permissions'].apply(lambda x: [permission.strip() for permission in x.split(',')] if isinstance(x, str) else [])
    return df

def display_statistics(df):
    permission_counts = Counter(permission for permissions in df['Permissions'] for permission in permissions)
    st.header('Permission Statistics')
    st.bar_chart(permission_counts)
    return permission_counts

def display_filter_section(df, permission_counts):
    st.header('Filter Personas by Permission')
    permission_list = list(permission_counts.keys())
    selected_permission = st.selectbox('Select a Permission', permission_list)
    filtered_df = df[df['Permissions'].apply(lambda x: selected_permission in x)]

    # Number of personas with this Permission
    num_personas = len(filtered_df)
    st.write(f"Number of personas with the permission '{selected_permission}': {num_personas}")

    # Permissions also controlling these personas
    other_permissions = Counter(permission for permissions in filtered_df['Permissions'] for permission in permissions if permission != selected_permission)
    st.write(f"Permissions also controlling these personas: {', '.join(other_permissions.keys())}")

    # Display the table of filtered personas
    st.write(filtered_df[['Name', 'Tags', 'Faction']])
    
    return df, selected_permission, permission_list

def edit_permissions(df, permission_list):
    st.header('Edit Permissions')
    permission_to_replace = st.selectbox('Permission to replace', permission_list)
    new_permission = st.text_input('New Permission')
    if st.button('Replace'):
        df['Permissions'] = df['Permissions'].apply(lambda x: [new_permission if p == permission_to_replace else p for p in x])
        st.success(f'Replaced {permission_to_replace} with {new_permission}')
        return True
    return False

def main():
    st.title('Persona Permissions Management')

    # File uploader
    uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])
    
    if uploaded_file:
        df = load_data(uploaded_file)
        while True:
            permission_counts = display_statistics(df)
            df, selected_permission, permission_list = display_filter_section(df, permission_counts)
            if edit_permissions(df, permission_list):
                continue
            break

if __name__ == "__main__":
    main()
