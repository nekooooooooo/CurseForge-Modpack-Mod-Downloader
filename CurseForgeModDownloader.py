import requests
import json
import os
import time
from tqdm import tqdm
from dotenv import load_dotenv
from os import environ
load_dotenv()

CURSEFORGE_API = environ.get('CURSEFORGE_API')
CURSEFORGE_URL = environ.get('CURSEFORGE_URL')

start = time.time()

headers = {
    'Accept': 'application/json',
    'x-api-key': CURSEFORGE_API
}

def downloadMod(url, path, fileName):
    resp = requests.get(url, stream=True)
    total = int(resp.headers.get('content-length', 0))
    with open(f"{path}/{fileName}", 'wb') as file, tqdm(
        desc=fileName,
        total=total,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in resp.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)

f = open('manifest.json')
print("Opening manifest.json")
manifest = json.load(f)

files = manifest['files']
modPackName = manifest['name']
modPackVersion = manifest['version']

folderName = f"{modPackName} {modPackVersion}"

downloadsPath = "./downloads/"
modpackPath = f"{downloadsPath}/{folderName}"

if not os.path.isdir(downloadsPath):
    os.mkdir(os.path.join(downloadsPath))

if not os.path.isdir(modpackPath):
    os.mkdir(os.path.join(modpackPath))

noOfMods = 0

for i in files:
    modId = i['projectID']
    fileId = i['fileID']
    
    r = requests.get(f'{CURSEFORGE_URL}/v1/mods/{modId}', headers=headers)
    mod = r.json()['data']

    modName = mod['name']
    modId = mod['id']
    modSummary = mod['summary']
    
    print(f'\nID: {modId}')
    print(f'Mod Name: {modName}')
    print(f'Summary: {modSummary}')

    files = mod['latestFilesIndexes']
    for file in files:
        if file['fileId'] == fileId:

            fileName = file['filename']
            downloadUrl = f"https://edge.forgecdn.net/files/{str(fileId)[:4]}/{str(fileId)[-3:]}/{fileName}"

            print(f'File ID: {fileId}')
            print(f'File Name: {fileName}')
            print(f'URL: {downloadUrl}')

            downloadMod(downloadUrl, modpackPath, fileName)

            break

        if file == files[-1]:
            print("Mod not found!")

    noOfMods += 1

end = time.time()

seconds = end - start

print(f"\n\nDownloaded {noOfMods} Mods in {seconds} second/s")
input("Press Enter to exit...")