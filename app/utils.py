import requests
from requests.auth import HTTPBasicAuth

import uuid
import base64



# --- EDC Configuration ---
# create generic asset creation request body:
def make_create_secure_asset_body(edc_asset_id, edc_asset_type, target_url, proxy_auth_header):
    """
    Inputs: 
        edc_asset_id        -   ID with which EDC registers the asset
        edc_asset_type      -   semantic identifier according to https://w3id.org/catenax/taxonomy#...
        target_url          -   path to the registered data object
        proxy_auth_header   -   header to internally access the datasource to which we proxy

    Outputs: 
        create_asset_body   -   Body for the creation or edit request
    """
    create_asset_body = {
        "@context": {
            "edc": "https://w3id.org/edc/v0.0.1/ns/",    
            "cx-common": "https://w3id.org/catenax/ontology/common#",    
            "cx-taxo": "https://w3id.org/catenax/taxonomy#",
            "dct": "http://purl.org/dc/terms/"  
        },
        "@id": edc_asset_id, 
        "properties": {    
            "dct:type": {
                "@id": "cx-taxo:" + edc_asset_type, 
                # examples: 
                # Submodel: "cx-taxo:Submodel"            or "https://w3id.org/catenax/taxonomy#Submodel
                # DTR:      "cx-taxo:DigitalTwinRegistry" or "https://w3id.org/catenax/taxonomy#DigitalTwinRegistry
                # Asset.    "cx-taxo:Asset"               or "https://w3id.org/catenax/taxonomy#Asset  
                },    
            "cx-common:version": "3.0"
        },
        "privateProperties": { },
        "dataAddress": {
            "@type":   "DataAddress",
            "type":    "HttpData",
            "baseUrl":  target_url,     
            # Proxy-cfg:
            "proxyMethod": "false",  
            "proxyQueryParams": "true",
            "proxyPath": "true",
            "header:Authorization": proxy_auth_header, # example: "Basic " + b64encoded string,
        },
    }

    # return
    return create_asset_body


# --- Policies ---
# create access policy:
def create_generic_Access_PolicyDefinitionRequest_body(access_policy_id, policy_group, policy_action="use"):
    access_policy_body = {
        "@context": [
            "https://w3id.org/tractusx/policy/v1.0.0",
            "http://www.w3.org/ns/odrl.jsonld",
            {
                "@vocab": "https://w3id.org/edc/v0.0.1/ns/"
            }
        ],
        "@type": "PolicyDefinitionRequest",
        "@id": access_policy_id, 
        "policy": {
            "@type": "Set",
            "permission": [
                {
                    "action": policy_action,
                    "constraint": [
                        {
                            "leftOperand": {
                                "@value": "BusinessPartnerNumber"                        
                                },
                            "operator": "eq",
                            "rightOperand": policy_group,
                        },
                    ]
                }
            ]    
        },
    }
    return access_policy_body


# create access policy:
def create_generic_Usage_PolicyDefinitionRequest_body(usage_policy_id, policy_action="use"):
    usage_policy_body = {
        "@context": [
            "https://w3id.org/tractusx/policy/v1.0.0",
            "http://www.w3.org/ns/odrl.jsonld",
            {
                "@vocab": "https://w3id.org/edc/v0.0.1/ns/"
            }
        ],
        "@type": "PolicyDefinitionRequest",
        "@id": usage_policy_id,
        "policy": {
            "@type": "Set",
            "permission": [
                {
                    "action": policy_action,
                    "constraint": [
                        {
                        "leftOperand": {
                            "@value": "https://factory-operator.com/terms/conditions"                        
                            },
                        "operator": "eq",
                        "rightOperand": "reproduce",
                        },
                    ]
                }
            ]    
        },
    }
    return usage_policy_body

# create binding contract:
def create_generic_ContractDefinitionRequest_body(asset_id, contract_id, access_policy_id, usage_policy_id):
  # NOTE: On creation, the EDC does not automatically check if a policy with the corresponding @id exists
  return {
    "@context": {
      "@vocab": "https://w3id.org/edc/v0.0.1/ns/"
    },
    "@type": "ContractDefinitionRequestDto",  # <- Dto?
    "@id":              contract_id,       
    "accessPolicyId":   access_policy_id,
    "contractPolicyId": usage_policy_id,
    "assetsSelector": [
      {
        "@type": "CriterionDto",
        "operandLeft": "https://w3id.org/edc/v0.0.1/ns/id",
        "operator": "=",
        "operandRight": asset_id,
      }
    ]
  }



# --- MISC Helpers ---
def print_edc_assets(res_get_assets):
    print(res_get_assets)
    if res_get_assets.status_code != 200:
        return

    print("{idx:8} {id:42} {assetType:28} {idshort:81}".format(idx="Index", id="id", assetType="assetType", idshort="baseUrl"))
    print("-"*8 + " " + "-"*42 + " " + "-"*28 + " " + "-"*81)

    for idx, retrived_asset in enumerate(res_get_assets.json()):
        print("{idx:8} {id:42} {assetType:28} {idshort:81}".format(idx=str(idx)+ ":", id=retrived_asset["@id"][0:81],
                                                                assetType=retrived_asset['properties']['http://purl.org/dc/terms/type']['@id'].split('/')[-1].split('#')[-1], 
                                                                idshort=retrived_asset["dataAddress"]['baseUrl']))
   
def print_shelldescriptors(res_descriptors):
    print(res_descriptors)
    if res_descriptors.status_code != 200:
        return

    print("{idx:8} {id:42} {idshort:42}".format(idx="Index", id="globalAssetId", idshort="idShort"))
    print("-"*8 + " " + "-"*42 + " " + "-"*42)

    for idx, descriptor in enumerate(res_descriptors.json()['result']):
        if "globalAssetId" in descriptor.keys():
            print("{idx:8} {id:42} {idshort:42}".format(idx=str(idx)+ ":", id=descriptor["globalAssetId"], idshort=descriptor["idShort"]))

def print_submodels(res_get_submodels):
    print(res_get_submodels)
    if res_get_submodels.status_code != 200:
        return

    print("{idx:8} {id:81} {idshort:42}".format(idx="Index", id="id", idshort="idShort"))
    print("-"*8 + " " + "-"*81 + " " + "-"*42)

    for idx, retrived_submodel in enumerate(res_get_submodels.json()['result']):
        print("{idx:8} {id:81} {idshort:42}".format(idx=str(idx)+ ":", id=retrived_submodel["id"][0:81], idshort=retrived_submodel["idShort"]))  



# --- Templates ---
def get_submodel_template():
    return {
        "idShort": "",
        "id": "",
        "semanticId": {
            "type": "ModelReference",
            "keys": [
                {
                    "type": "Submodel",
                    "value": "https://admin-shell.io/sinksubmodel"
                }
            ]
        },
        "submodelElements": [],
        "modelType": "Submodel"
    }

def get_submodel_element_blob_template():
    return {
        "idShort": "",
        "id": "",
        "value": "",
        "semanticId": {
            "type": "ModelReference",
            "keys": [
                {
                    "type": "GlobalReference",
                    "value": "0173-1#02-AAM556#002"
                }
            ]
        },
        "contentType": "application/str",
        "modelType": "Blob"
    }