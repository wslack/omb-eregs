import argparse
import csv
import logging
import sys
from datetime import datetime

from django.core.management.base import BaseCommand

from reqs.models import (Keyword, KeywordConnect, Policy, PolicyTypes,
                         Requirement)

logger = logging.getLogger(__name__)


def convert_omb_policy_id(string):
    if string in ('NA', 'None'):
        return ''
    return string


def convert_policy_type(string):
    """Raises a ValueError if the string type can't be found"""
    if 'memo' in string.lower():
        return PolicyTypes.memorandum
    elif 'circular' in string.lower():
        return PolicyTypes.circular
    return PolicyTypes(string)


def convert_date(string):
    """Tries to convert a date string into a date. Accounts for NA. May raise
    a ValueError"""
    if string not in ('NA', 'None specified'):
        return datetime.strptime(string, '%m/%d/%Y').date()


class PolicyProcessor:
    """Creates/updates and tracks Policy objects based on the data found in
    CSV rows"""
    def __init__(self):
        self.policies = {}

    def from_row(self, row):
        """Retrieve/create/update a Policy object"""
        policy_number = int(row['policyNumber'])
        if policy_number not in self.policies:
            params = {
                'policy_number': policy_number,
                'title': row['policyTitle'],
                'uri': row['uriPolicyId'],
                'omb_policy_id': convert_omb_policy_id(row['ombPolicyId']),
                'policy_type': convert_policy_type(row['policyType']).value,
                'issuance': convert_date(row['policyIssuanceYear']),
                'sunset': convert_date(row['policySunset'])
            }
            policy, _ = Policy.objects.update_or_create(
                policy_number=policy_number, defaults=params)
            self.policies[policy_number] = policy
        return self.policies[policy_number]


def priority_split(text, *splitters):
    """When we don't know which character is being used to combine text, run
    through a list of potential splitters and split on the first"""
    present = [s for s in splitters if s in text]
    # fall back to non-present splitter; ensures we have a splitter
    splitters = present + list(splitters)
    splitter = splitters[0]
    return [seg.strip() for seg in text.split(splitter) if seg.strip()]


class KeywordProcessor:
    """Creates or retrieves Keyword models"""
    def __init__(self):
        self.cache = {}

    @staticmethod
    def keywords(row):
        to_return = []
        for field, value in row.items():
            if field == 'Other (Keywords)':
                to_return.extend(priority_split(value, ';', ','))
            elif '(Keywords)' in field and value:
                to_return.append(field.replace('(Keywords)', '').strip())
        return to_return

    def connections(self, row, req_pk):
        for keyword in self.keywords(row):
            if keyword not in self.cache:
                self.cache[keyword] = Keyword.objects.get_or_create(
                    name=keyword)[0].pk
            yield KeywordConnect(tag_id=self.cache[keyword],
                                 content_object_id=req_pk)


class RowProcessor:
    """Creates Requirement objects, Policies, and Keyword connections,
    raising exceptions if something goes wrong with the process."""
    def __init__(self):
        self.policies = PolicyProcessor()
        self.keywords = KeywordProcessor()
        self.connections = []
        self.req_ids = set()

    def add(self, row):
        req_id = row['reqId']
        if req_id in self.req_ids:
            raise ValueError("Req ID already seen: {0}".format(req_id))

        params = dict(
            policy=self.policies.from_row(row),
            req_id=req_id,
            issuing_body=row['issuingBody'],
            policy_section=row['policySection'],
            policy_sub_section=row['policySubSection'],
            req_text=row['reqText'],
            verb=row['verb'],
            impacted_entity=row['Impacted Entity'],
            req_deadline=row['reqDeadline'],
            citation=row['citation'],
        )
        req, _ = Requirement.objects.update_or_create(
            req_id=req_id, defaults=params)
        self.connections.extend(self.keywords.connections(row, req.pk))
        self.req_ids.add(req_id)


class Command(BaseCommand):
    help = 'Populate requirements from a CSV'   # noqa

    def add_arguments(self, parser):
        parser.add_argument(
            'input_file', nargs='?', type=argparse.FileType('r'),
            default=sys.stdin)

    def handle(self, *args, **options):
        rows = RowProcessor()
        for idx, row in enumerate(csv.DictReader(options['input_file'])):
            if idx % 100 == 0:
                logger.info('Processing row %s', idx)
            try:
                rows.add(row)
            except ValueError as err:
                logger.warning("Problem with this row %s: %s", idx, err)
        # Delete all keyword connections which may exist in the DB
        KeywordConnect.objects.filter(
            content_object__req_id__in=rows.req_ids).delete()
        KeywordConnect.objects.bulk_create(rows.connections)
