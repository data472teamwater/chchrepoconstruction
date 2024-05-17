import logging
import azure.functions as func
from bs4 import BeautifulSoup
import pandas as pd
import requests
from sqlalchemy import create_engine

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="http_trigger")
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function started.')

    try:
        url = 'https://ccc.govt.nz/transport/improving-our-transport-and-roads/works'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        ID = 1

        # Connection string
        connection_string = 'mssql+pyodbc://metrobusadmin:Route%23001@metrobusdbserver.database.windows.net/metrobusdb?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&TrustServerCertificate=no&Connection+Timeout=30'

        # Create SQLAlchemy engine
        engine = create_engine(connection_string, fast_executemany=True)

        # Find all <a> tags with href attribute
        links = [link.get('href') for link in soup.find_all('a', href=True)]
        transport_links = []
        for link in links:
            if '/transport/works-3' in link:
                transport_links.append('https://ccc.govt.nz' + link)

        static_maps = []
        for link in transport_links:
            if(get_static_maps_links(link) is not None):
                static_maps.append(get_static_maps_links(link))

        # Data dictionary for construction sites
        dict_const = {
            "site_no": [],
            "site_pt_lat": [],
            "site_pt_lon": []
        }

        for link in static_maps:
            data = get_coordinates(link, ID)
            if data != None:
                dict_const["site_no"].extend(data["Construction ID"])
                dict_const["site_pt_lat"].extend(data["Latitude"])
                dict_const["site_pt_lon"].extend(data["Longitude"])
                ID += 1

        # Convert dictionary to DataFrame
        df_const = pd.DataFrame(dict_const)

        # Table name for data storage in SQL Database
        table_name = "constructionsites"

        # Push DataFrame to Azure SQL Database
        df_const.to_sql(table_name, engine, if_exists='replace', index=False)

        logging.info('Python HTTP trigger function executed successfully.')

        return func.HttpResponse("Data updated successfully.", status_code=200)

    except Exception as e:
        logging.error(f'An error occurred: {str(e)}')
        return func.HttpResponse("An error occurred while updating data.", status_code=500)

    finally:
        # Close the connection
        engine.dispose()

def get_all_links(url):
    response = requests.get(url)
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    src_links = soup.find_all(src=True)
    all_links = []
    for link in src_links:
        all_links.append(link['src'])
    return all_links

def get_static_maps_links(url):
    static_map_links = [s for s in get_all_links(url) if 'staticmap' in s]
    for i in static_map_links:
        return i
    return None

def extract_coordinates_from_url(api_url, ID):
    try:
        if not api_url:
            logging.error("Error: API URL is empty or None.")
            return None
        coordinates_part = "path=color:0x0000ff%7Cweight:5%7C"
        if coordinates_part not in api_url:
            return None
        else:
            coordinates_part = api_url.split(coordinates_part)[1].split("&")[0]
            coordinates_list = coordinates_part.split("%7C")
            coordinates = [(float(coord.split(",")[0]), float(coord.split(",")[1])) for coord in coordinates_list]
            coordinates = list(set(coordinates))
            return coordinates
    except Exception as e:
        logging.error(f'Error extracting coordinates: {str(e)}')
        return None

def get_coordinates(url, ID):
    coordinates = extract_coordinates_from_url(url, ID)
    lat_data = []
    lon_data = []
    const_id = []
    if coordinates:
        for coordinate in coordinates:
            lat_data.append(coordinate[0])
            lon_data.append(coordinate[1])
            const_id.append(ID)
        dict_const = {
            "Construction ID": const_id,
            "Latitude": lat_data,
            "Longitude": lon_data
        }
        return dict_const
    else:
        return None