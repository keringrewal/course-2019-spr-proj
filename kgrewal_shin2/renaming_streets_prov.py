# http://datamechanics.io/data/boston_street_names.json

import urllib.request
import json
import dml
import prov.model
import datetime
import uuid


class ProvenanceModel(dml.Algorithm):
    contributor = 'kgrewal_shin2'
    reads = []
    writes = ['kgrewal_shin2.street_names', 'kgrewal_shin2.landmarks']

    @staticmethod
    def execute(trial=False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('kgrewal_shin2', 'kgrewal_shin2')

        url = 'http://datamechanics.io/data/boston_street_names.json'
        response = urllib.request.urlopen(url).read().decode("utf-8")
        r = json.loads(response)
        s = json.dumps(r, sort_keys=True, indent=2)
        repo.dropCollection("street_names")
        repo.createCollection("street_names")
        repo['kgrewal_shin2.street_names'].insert_many(r)
        repo['kgrewal_shin2.street_names'].metadata({'complete': True})
        print(repo['kgrewal_shin2.street_names'].metadata())

        url = 'http://datamechanics.io/data/boston_landmarks.json'
        response = urllib.request.urlopen(url).read().decode("utf-8")
        r = json.loads(response)
        s = json.dumps(r, sort_keys=True, indent=2)
        repo.dropCollection("landmarks")
        repo.createCollection("landmarks")
        repo['kgrewal_shin2.landmarks'].insert_many(r)
        repo['kgrewal_shin2.landmarks'].metadata({'complete': True})
        print(repo['kgrewal_shin2.landmarks'].metadata())

        repo.logout()

        endTime = datetime.datetime.now()

        return {"start": startTime, "end": endTime}

    @staticmethod
    def provenance(doc=prov.model.ProvDocument(), startTime=None, endTime=None):
        '''
            Create the provenance document describing everything happening
            in this script. Each run of the script will generate a new
            document describing that invocation event.
            '''

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('kgrewal_shin2', 'kgrewal_shin2')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont',
                          'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.
        doc.add_namespace('bdp', 'https://data.cityofboston.gov/resource/')

        this_script = doc.agent('alg:kgrewal_shin2#street_name_prov',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource = doc.entity('bdp:wc8w-nujj',
                              {'prov:label': '311, Service Requests', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'json'})
        get_street_name = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        get_landmarks = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)

        doc.wasAssociatedWith(get_street_name, this_script)
        doc.usage(get_street_name, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query': '?type=Street+Name&$select=full_name,gender,zipcodes,rank,street_name'
                   }
                  )

        doc.usage(get_landmarks, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  'ont:Query':'?type=Landmark+Name&$select=Name of Property,Address,Neighborhood'
                  }
                  )

        streets = doc.entity('dat:kgrewal_shin2#street_name',
                          {prov.model.PROV_LABEL: 'Boston Streets', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(streets, this_script)
        doc.wasGeneratedBy(streets, get_street_name, endTime)
        doc.wasDerivedFrom(streets, resource, get_street_name, get_street_name, get_street_name)

        landmarks = doc.entity('dat:kgrewal_shin2#landmarks',
                          {prov.model.PROV_LABEL: 'Boston Landmarks', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(landmarks, this_script)
        doc.wasGeneratedBy(landmarks, get_landmarks, endTime)
        doc.wasDerivedFrom(landmarks, resource, get_landmarks, get_landmarks, get_landmarks)

        repo.logout()

        return doc


# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
ProvenanceModel.execute()
doc = ProvenanceModel.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))

## eof