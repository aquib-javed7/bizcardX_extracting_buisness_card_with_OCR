import streamlit as st
from streamlit_option_menu import option_menu
import easyocr
from PIL import Image
import pandas as pd
import numpy as np
import re
import io
import psycopg2

def image_to_text(path):

    input_image=Image.open(path)

    #Converting image to array format
    image_arr=np.array(input_image)

    reader=easyocr.Reader(['en'])
    text=reader.readtext(image_arr, detail=0)

    return text, input_image

def extracted_text(texts):

    extract_dict={'NAME':[],'DESIGNATION':[],'COMPANY_NAME':[],'CONTACT':[],'EMAIL':[],'WEBSITE':[],'ADDRESS':[],'PINCODE':[]}

    extract_dict['NAME'].append(texts[0])
    extract_dict['DESIGNATION'].append(texts[1])

    for i in range(2,len(texts)):

        if texts[i].startswith('+') or (texts[i].replace('-','').isdigit() and '-' in texts[i]):
            extract_dict['CONTACT'].append(texts[i])
        
        elif '@' in texts[i] and '.com' in texts[i]:
            extract_dict['EMAIL'].append(texts[i])

        elif 'WWW' in texts[i] or 'www' in texts[i] or 'Www' in texts[i] or 'wWw' in texts[i] or 'wwW' in texts[i]:
            small=texts[i].lower()
            extract_dict['WEBSITE'].append(small)

        elif 'Tamil Nadu' in texts[i] or 'TamilNadu' in texts[i] or texts[i].isdigit():
            extract_dict['PINCODE'].append(texts[i])

        elif re.match(r'^[A-Za-z]', texts[i]):
            extract_dict['COMPANY_NAME'].append(texts[i])
        
        else:
            remove_colon=re.sub(r'[,;]','',texts[i])
            extract_dict['ADDRESS'].append(remove_colon)

    for key,value in extract_dict.items():
        if len(value)>0:
            concadenate=' '.join(value)
            extract_dict[key]=[concadenate]

        else:
            value='NA'
            extract_dict[key]=[value] 
    
    return extract_dict


#Stresmlit Part

st.set_page_config(page_title="BizcardX With OCR", page_icon="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ8ELw5nOfVqYFjDgffUH89Bbh9ANMmFFMtASGzoND1yoCxrEYAlVi00HXNpo_gs_2ejRM&usqp=CAU")

# Set background image URL (you can replace this with your image URL)
background_image_url = "https://i.etsystatic.com/14280200/r/il/10cfc9/1640926329/il_fullxfull.1640926329_15u9.jpg"  

# Custom CSS to set background image for the entire page
st.markdown(f"""
    <style>
        body {{
            background-image: url("{background_image_url}");
            background-size: cover;  /* Ensures the image covers the entire page */
            background-repeat: no-repeat;  /* Ensures the image does not repeat */
            background-attachment: fixed;  /* Makes the background fixed when scrolling */
            color: white;  /* Text color set to white for contrast against background */
        }}
        .stApp {{
            background-color: transparent;
        }}
        .css-1v0mbp5 {{
            background-color: rgba(255, 255, 255, 0.7);  /* Make the option menu background semi-transparent */
            border-radius: 10px;  /* Optional: round the corners of the menu */
        }}
    </style>
""", unsafe_allow_html=True)

# Title for the app
st.markdown("<h1 style='text-align:center;text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5); color:#8bb933; font-size:50px;'>BizCardX: Extracting Business Card Data with OCR</h1>", unsafe_allow_html=True)

# Create the option menu

#option menu

selected = option_menu(
    menu_title=None,
    options=["Image","Delete","Contact"],
    icons=["image","trash","at"],
    default_index=0,
    orientation="horizontal"
)

if selected =='Image':
    
    img = st.file_uploader('Upload the Image',type=['png','jpg','jpeg'])

    if img is not None:
        st.image(img,width=300)

        text_image,input_image=image_to_text(img)

        text_dict=extracted_text(text_image)

        if text_dict:
            st.success('TEXT IS EXTRACTED SUCCESSFULLY')
        
        df=pd.DataFrame(text_dict)
    
        #Converting image to Bytes
        
        Image_bytes=io.BytesIO()
        input_image.save(Image_bytes, format='PNG')

        image_data= Image_bytes.getvalue()

        #Creating Dictionary

        data={'Image':[image_data]}

        df_1=pd.DataFrame(data)

        concat_df=pd.concat([df,df_1],axis=1)

        st.dataframe(concat_df)

        button_1=st.button('Save', use_container_width=True)

        if button_1:

            mydb=psycopg2.connect(host='localhost',
                            user='postgres',
                            password='1234',
                            database='bizcardx_data',
                            port='5432')
            cursor=mydb.cursor()

            create_query='''create table if not exists bizcard_details(name varchar(225),
                                                                    designation varchar(225),
                                                                    company_name varchar (225),
                                                                    contact varchar (225),
                                                                    email varchar (225),
                                                                    website text,
                                                                    address text,
                                                                    pincode varchar (225),
                                                                    image text
                                                                    )'''
            cursor.execute(create_query)
            mydb.commit()

            #insert query

            insert_query='''insert into bizcard_details(name,
                                                    designation,
                                                    company_name,
                                                    contact,
                                                    email,
                                                    website,
                                                    address,
                                                    pincode,
                                                    image)
                                                    
                                                    values(%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
            
            datas=concat_df.values.tolist()[0] 

            cursor.execute(insert_query,datas)
            mydb.commit()

            st.success('SAVED SUCCESSFULLY')

    method=st.radio("Select the Method",['None','Preview','Modify'])

    if method == 'None':
        st.write('')

    if method == 'Preview':

        mydb=psycopg2.connect(host='localhost',
                                user='postgres',
                                password='1234',
                                database='bizcardx_data',
                                port='5432')
        cursor=mydb.cursor()

        #select Query

        select_query='SELECT * FROM bizcard_details'

        cursor.execute(select_query)
        table_1=cursor.fetchall()
        mydb.commit()

        table_df=pd.DataFrame(table_1,columns=['NAME','DESIGNATION','COMPANY_NAME','CONTACT','EMAIL','WEBSITE','ADDRESS','PINCODE','IMAGE'])

        st.dataframe(table_df)

    elif method == 'Modify':

        mydb=psycopg2.connect(host='localhost',
                                user='postgres',
                                password='1234',
                                database='bizcardx_data',
                                port='5432')
        cursor=mydb.cursor()

        #select Query

        select_query='SELECT * FROM bizcard_details'

        cursor.execute(select_query)
        table_1=cursor.fetchall()
        mydb.commit()

        table_df=pd.DataFrame(table_1,columns=['NAME','DESIGNATION','COMPANY_NAME','CONTACT','EMAIL','WEBSITE','ADDRESS','PINCODE','IMAGE'])

        col1,col2 = st.columns(2)
        with col1:
            selected_name= st.selectbox('Select the Name', table_df['NAME'])

        df_3= table_df[table_df['NAME'] == selected_name]

        df_4= df_3.copy()

        col1,col2 = st.columns(2)
        with col1:
            mo_name= st.text_input('Name',df_3['NAME'].unique()[0])
            mo_desi= st.text_input('Designation',df_3['DESIGNATION'].unique()[0])
            mo_comna= st.text_input('Comapany_Name',df_3['COMPANY_NAME'].unique()[0])
            mo_cont= st.text_input('Contact',df_3['CONTACT'].unique()[0])
            mo_emai= st.text_input('Email',df_3['EMAIL'].unique()[0])

            df_4['NAME']=mo_name
            df_4['DESIGNATION']=mo_desi
            df_4['COMPANY_NAME']=mo_comna
            df_4['CONTACT']=mo_cont
            df_4['EMAIL']=mo_emai
        
        with col2:
            mo_webst= st.text_input('Website',df_3['WEBSITE'].unique()[0])
            mo_addres= st.text_input('Address',df_3['ADDRESS'].unique()[0])
            mo_pinco= st.text_input('Pincode',df_3['PINCODE'].unique()[0])
            mo_image= st.text_input('Image',df_3['IMAGE'].unique()[0])

            df_4['WEBSITE']=mo_webst
            df_4['ADDRESS']=mo_addres
            df_4['PINCODE']=mo_pinco
            df_4['IMAGE']=mo_image

        st.dataframe(df_4)

        col1,col2 = st.columns(2)
        with col1:
            button_3=st.button('Modify', use_container_width=True)
        
        if button_3:

            mydb=psycopg2.connect(host='localhost',
                                user='postgres',
                                password='1234',
                                database='bizcardx_data',
                                port='5432')
            cursor=mydb.cursor()

            cursor.execute(f"DELETE FROM bizcard_details WHERE NAME = '{selected_name}'")
            mydb.commit()

            #insert query

            insert_query='''insert into bizcard_details(name,
                                                    designation,
                                                    company_name,
                                                    contact,
                                                    email,
                                                    website,
                                                    address,
                                                    pincode,
                                                    image)
                                                    
                                                    values(%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
            
            datas=df_4.values.tolist()[0]
 
            cursor.execute(insert_query,datas)
            mydb.commit()

            st.success('MODIFIED SUCCESSFULLY')


if selected =='Delete':
    mydb=psycopg2.connect(host='localhost',
                                user='postgres',
                                password='1234',
                                database='bizcardx_data',
                                port='5432')
    cursor=mydb.cursor()

    col1,col2 = st.columns(2)
    with col1:
        
        select_query='SELECT NAME FROM bizcard_details'
        cursor.execute(select_query)
        table_1=cursor.fetchall()
        mydb.commit()

        name=[]

        for i in table_1:
            name.append(i[0])
        
        name_select= st.selectbox('Select the Name', name)
    
    with col2:

        select_query=F"SELECT DESIGNATION FROM bizcard_details WHERE NAME = '{name_select}'"
        cursor.execute(select_query)
        table_2=cursor.fetchall()
        mydb.commit()

        designation=[]

        for j in table_2:
            designation.append(j[0])
        
        designation_select= st.selectbox('Select the Designation', designation)

    if name_select and designation_select:
        col1,col2,col3=st.columns(3)

        with col1:
            st.write(f'Selected Name : {name_select}')
            st.write('')
            st.write('')
            st.write('')
            st.write(f'Selected Designation : {designation_select}')

        with col2:
            st.write('')
            st.write('')
            st.write('')
            st.write('')
            st.write('')
            st.write('')

            remove= st.button('Delete', use_container_width=True)

            if remove:

                cursor.execute(f"DELETE FROM bizcar_details WHERE NAME ='{name_select}' and DESIGNATION = '{designation_select}'")
                mydb.commit()

                st.warning('DELETED')

if selected == 'Contact':
    # Data
    name = "Akib Javith VST"
    mail = "aquibjaved04@gmail.com"
    description = "An Aspiring DATA-SCIENTIST..!"
    social_media = {
        "GITHUB": "https://github.com/aquib-javed7",
        "LINKEDIN": "https://www.linkedin.com/in/akib-javith-37bbbb324/"
    }

    # Columns for layout
    col1, col2 = st.columns(2)

    # Using the second column to display title, description, and email
    with col2:
        st.markdown("<h1 style='color:#8bb933; font-size:50px;text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);'>BizCardX: Extracting Business Card Data with OCR</h1>", unsafe_allow_html=True)
        st.write("""
            BizCardX is to automate and simplify the process of capturing and managing contact information from business cards, 
            saving users time and effort. It is particularly useful for professionals who frequently attend networking events, 
            conferences, and meetings where they receive numerous business cards that need to be converted into digital contacts.
        """, unsafe_allow_html=True)
        
        # Divider line
        st.write("---")
        
    st.markdown(f"<h3 style='color:#8bb933;text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.5);'>Mail: <a href='mailto:{mail}' style='color:white;'>{mail}</a></h3>", unsafe_allow_html=True)

    # Space between sections
    st.write("#")

    # Display social media links with green color
    cols = st.columns(len(social_media))
    for index, (platform, link) in enumerate(social_media.items()):
        with cols[index]:
            st.markdown(f'<a href="{link}" target="_blank" style="color:white;text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.5); font-size: 20px;">{platform}</a>', unsafe_allow_html=True)