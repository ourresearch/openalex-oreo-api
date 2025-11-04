
from functools import wraps
from numbers import Number


"""
Test Helpers
"""
def expects_numbers_bug(func):
  @wraps(func)
  def wrapper(prod_value, walden_value):
    if isinstance(prod_value, Number) and not isinstance(walden_value, Number):
      return True # If prod has a number and Walden doesn't then it's a bug
    
    if not isinstance(prod_value, Number) or not isinstance(walden_value, Number):
      return False
        
    return func(prod_value, walden_value)
  return wrapper


def expects_numbers_feature(func):
  @wraps(func)
  def wrapper(prod_value, walden_value):
    if not isinstance(prod_value, Number) and isinstance(walden_value, Number):
      return True # If prod doesn't have a number and Walden does then it's a feature

    if not isinstance(prod_value, Number) or not isinstance(walden_value, Number):
      return False
        
    return func(prod_value, walden_value)
  return wrapper


def expects_strings_bug(func):
  @wraps(func)
  def wrapper(prod_value, walden_value):
    if isinstance(prod_value, str) and not isinstance(walden_value, str):
      return True # If prod has a string and Walden doesn't then it's a bug
    
    if not isinstance(prod_value, str) or not isinstance(walden_value, str):
      return False
        
    return func(prod_value, walden_value)
  return wrapper


def expects_lists_bug(func):
  @wraps(func)
  def wrapper(prod_value, walden_value):
    if isinstance(prod_value, list) and not isinstance(walden_value, list):
      return True # If prod has a list and Walden doesn't then it's a bug
    
    if not isinstance(prod_value, list) or not isinstance(walden_value, list):
      return False
        
    return func(prod_value, walden_value)
  return wrapper


def expects_lists_feature(func):
  @wraps(func)
  def wrapper(prod_value, walden_value):
    if not isinstance(prod_value, list) or not isinstance(walden_value, list):
      return False
        
    return func(prod_value, walden_value)
  return wrapper

def is_set_test(func):
  return func in [set_does_not_equal, set_count_does_not_equal, set_count_increased, set_count_decreased]


def get_test_keys(entity, type_="all"):
  if type_ == "all":
    tests = tests_schema[entity]
  elif type_ == "bug":
    tests = [test for test in tests_schema[entity] if test["test_type"] == "bug"]
  elif type_ == "feature":
    tests = [test for test in tests_schema[entity] if test["test_type"] == "feature"]

  return [test["display_name"].replace(" ", "_").lower() for test in tests]


"""
Test Functions
"""
def not_exact_match(prod_value, walden_value):
  return prod_value != walden_value


@expects_numbers_feature
def greater_than(prod_value, walden_value):
  return walden_value > prod_value


@expects_numbers_feature
def greater_than_or_equal(prod_value, walden_value):
  return walden_value >= prod_value


@expects_numbers_bug
def less_than(prod_value, walden_value):
  return walden_value < prod_value


def within_5_percent(prod_value, walden_value):  
  if prod_value == 0 and walden_value == 0:
      return True

  if prod_value == 0:
      return False

  return abs((walden_value - prod_value) / prod_value * 100) <= 5


def within_10_percent(prod_value, walden_value):  
  if prod_value == 0 and walden_value == 0:
      return True

  if prod_value == 0:
      return False

  return abs((walden_value - prod_value) / prod_value * 100) <= 10


def within_20_percent(prod_value, walden_value):  
  if prod_value == 0 and walden_value == 0:
      return True

  if prod_value == 0:
      return False

  return abs((walden_value - prod_value) / prod_value * 100) <= 20


def within_50_percent(prod_value, walden_value):  
  if prod_value == 0 and walden_value == 0:
      return True

  if prod_value == 0:
      return False

  return abs((walden_value - prod_value) / prod_value * 100) <= 50


@expects_numbers_bug
def below_5_percent(prod_value, walden_value):
  return prod_value > walden_value and not within_5_percent(prod_value, walden_value)


@expects_numbers_feature
def above_5_percent(prod_value, walden_value):
  return walden_value > prod_value and not within_5_percent(prod_value, walden_value)


@expects_strings_bug
def length_not_within_5_percent(prod_value, walden_value):
  return not within_5_percent(len(prod_value), len(walden_value))


@expects_numbers_bug
def not_within_10_percent(prod_value, walden_value):
  return not within_10_percent(prod_value, walden_value)


@expects_numbers_bug
def not_within_20_percent(prod_value, walden_value):
  return not within_20_percent(prod_value, walden_value)


@expects_numbers_bug
def not_within_50_percent(prod_value, walden_value):
  return not within_50_percent(prod_value, walden_value)


@expects_lists_bug
def count_does_not_equal(prod_value, walden_value):
  return len(prod_value) != len(walden_value)


@expects_lists_feature
def count_increased_from_zero(prod_value, walden_value):
  return len(prod_value) == 0 and len(walden_value) > 0


def count_increased_from_null_above_zero(prod_value, walden_value):
  return prod_value is None and isinstance(walden_value, list) and len(walden_value) > 0


@expects_lists_feature
def count_decreased_from_zero(prod_value, walden_value):
  return len(prod_value) > 0 and len(walden_value) == 0

@expects_lists_bug
def set_does_not_equal(prod_value, walden_value):
  return set(prod_value) != set(walden_value)


@expects_lists_feature
def set_equals(prod_value, walden_value):
  return set(prod_value) == set(walden_value)


@expects_lists_bug
def set_count_does_not_equal(prod_value, walden_value):
  return len(set(prod_value)) != len(set(walden_value))


@expects_lists_feature
def set_count_increased(prod_value, walden_value):
  return len(set(prod_value)) < len(set(walden_value))


@expects_lists_bug
def set_count_decreased(prod_value, walden_value):
  return len(set(prod_value)) > len(set(walden_value))


def status_changed_except_gold(prod_value, walden_value):
  return walden_value != "gold" and prod_value != walden_value


def status_became_gold(prod_value, walden_value):
  return prod_value != "gold" and walden_value == "gold"


def became_false(prod_value, walden_value):
  return walden_value is False and prod_value is not False


def became_null(prod_value, walden_value):
  return walden_value is None and prod_value is not None


def became_true(prod_value, walden_value):
  return walden_value is True and prod_value is not True


def value_lost(prod_value, walden_value):
  return prod_value is not None and walden_value is None


def value_added(prod_value, walden_value):
  return prod_value is None and walden_value is not None


def existing_value_changed(prod_value, walden_value):
  """ True if prod had a value that changed, but False if walden adds a value where prod had none"""
  return prod_value is not None and prod_value != walden_value


@expects_lists_bug
def set_lost_items(prod_value, walden_value):
  """ True if prod had items that are no longer in walden (allows additions, fails on removals) """
  prod_set = set(prod_value)
  walden_set = set(walden_value)
  return not prod_set.issubset(walden_set)


def language_changed_to_non_english(prod_value, walden_value):
  return prod_value == "en" and walden_value != "en" and walden_value is not None


def language_changed_from_value_to_english(prod_value, walden_value):
  return prod_value and prod_value != "en" and walden_value == "en"


def type_changed_to_repository(prod_value, walden_value):
  return prod_value != "repository" and walden_value == "repository"


def type_changed_from_funder(prod_value, walden_value):
  return prod_value == "funder" and walden_value != "funder"


"""
TEST DEFINITIONS
"""
tests_schema_base = {
  "works": [
    # Sources
    {
      "display_name": "Primary Source Lost",
      "field": "primary_location.source.id",
      "field_type": "string",
      "test_func": value_lost,
      "test_type": "bug",
      "category": "sources",
      "description": "The <code>primary_location.source.id</code> field had a value but now is null or missing",
    },
    {
      "display_name": "Primary Source Added",
      "field": "primary_location.source.id",
      "field_type": "string",
      "test_func": value_added,
      "test_type": "feature",
      "category": "sources",
      "description": "The <code>primary_location.source.id</code> field was missing but now has a value",
    },
    {
      "display_name": "Primary Source Changed",
      "field": "primary_location.source.id",
      "field_type": "string",
      "test_func": existing_value_changed,
      "test_type": "bug",
      "category": "sources",
      "description": "The <code>primary_location.source.id</code> field had a value and changed",
    },
    # Open Access
    {
      "display_name": "is_oa Added",
      "field": "open_access.is_oa",
      "field_type": "boolean",
      "test_func":  became_true,
      "test_type": "feature",
      "category": "open access",
      "description": "The <code>open_access.is_oa</code> field became <code>true</code>",
    },
    {
      "display_name": "is_oa Lost",
      "field": "open_access.is_oa",
      "field_type": "boolean",
      "test_func": became_false,
      "test_type": "bug",
      "category": "open access",
      "description": "The <code>open_access.is_oa</code> field became <code>false</code>",
    },
    {
      "display_name": "OA Status Changed",
      "field": "open_access.oa_status",
      "field_type": "string",
      "test_func": status_changed_except_gold,
      "test_type": "feature",
      "category": "open access",
      "description": "The <code>open_access.oa_status</code> field changed to a value other than <code>gold</code>",
    },
    {
      "display_name": "OA Status Changed to Gold",
      "field": "open_access.oa_status",
      "field_type": "string",
      "test_func": status_became_gold,
      "test_type": "feature",
      "category": "open access",
      "description": "The <code>open_access.oa_status</code> field changed to <code>gold</code>",
    },
    {
      "display_name": "PDF URL Lost",
      "field": "best_oa_location.pdf_url",
      "field_type": "string",
      "test_func": value_lost,
      "test_type": "bug",
      "category": "open access",
      "description": "The <code>best_oa_location.pdf_url</code> field was not null but now is null or missing",
    },
    {
      "display_name": "PDF URL Added",
      "field": "best_oa_location.pdf_url",
      "field_type": "string",
      "test_func": value_added,
      "test_type": "feature",
      "category": "open access",
      "description": "The <code>best_oa_location.pdf_url</code> field was missing but now has a value",
    },
    {
      "display_name": "Best OA License Changed",
      "field": "best_oa_location.license",
      "field_type": "string",
      "test_func": existing_value_changed,
      "test_type": "bug",
      "category": "open access",
      "description": "The <code>best_oa_location.license</code> field had a value and the value changed",
    },
    {
      "display_name": "Best OA License Lost",
      "field": "best_oa_location.license",
      "field_type": "string",
      "test_func": value_lost,
      "test_type": "bug",
      "category": "open access",
      "description": "The <code>best_oa_location.license</code> field was not null but now is null or missing",
    },
    {
      "display_name": "Best OA License Added",
      "field": "best_oa_location.license",
      "field_type": "string",
      "test_func": value_added,
      "test_type": "feature",
      "category": "open access",
      "description": "The <code>best_oa_location.license</code> field was missing but now has a value",
    },
    # Language
    {
      "display_name": "Language Changed to Non-English",
      "field": "language",
      "field_type": "string",
      "test_func": language_changed_to_non_english,
      "test_type": "feature",
      "category": "language",
      "description": "The <code>language</code> field changed to a non-English value",
    },
    {
      "display_name": "Language Added",
      "field": "language",
      "field_type": "string",
      "test_func": value_added,
      "test_type": "feature",
      "category": "language",
      "description": "The <code>language</code> field was missing but now has a value",
    },
    {
      "display_name": "Language Changed to English",
      "field": "language",
      "field_type": "string",
      "test_func": language_changed_from_value_to_english,
      "test_type": "bug",
      "category": "language",
      "description": "The <code>language</code> field changed from a non null value to English",
    },
    {
      "display_name": "Language Lost",
      "field": "language",
      "field_type": "string",
      "test_func": value_lost,
      "test_type": "bug",
      "category": "language",
      "description": "The <code>language</code> field was not null but now is null or missing",
    },
    # Locations
    {
      "display_name": "Locations Count Increased",
      "field": "locations_count",
      "field_type": "number",
      "test_func": greater_than,
      "test_type": "feature",
      "category": "locations",
      "description": "The <code>locations_count</code> field increased",
    },
    {
      "display_name": "Locations Count Decreased",
      "field": "locations_count",
      "field_type": "number",
      "test_func": less_than,
      "test_type": "bug",
      "category": "locations",
      "description": "The <code>locations_count</code> field decreased",
    },
    # Citations
    {
      "display_name": "Referenced Works Count Decreased",
      "field": "referenced_works_count",
      "field_type": "number",
      "test_func": below_5_percent,
      "test_type": "bug",
      "category": "citations",
      "description": "The <code>referenced_works_count</code> field decreased by 5% or more",
    },
    {
      "display_name": "Referenced Works Count Increased",
      "field": "referenced_works_count",
      "field_type": "number",
      "test_func": greater_than,
      "test_type": "feature",
      "category": "citations",
      "description": "The <code>referenced_works_count</code> field increased",
    },
    {
      "display_name": "Citations Count Decreased",
      "field": "cited_by_count",
      "field_type": "number",
      "test_func": less_than,
      "test_type": "bug",
      "category": "citations",
      "description": "The <code>cited_by_count</code> field decreased",
    },
    {
      "display_name": "Citations Count Increased",
      "field": "cited_by_count",
      "field_type": "number",
      "test_func": greater_than,
      "test_type": "feature",
      "category": "citations",
      "description": "The <code>cited_by_count</code> field increased",
    },
    {
      "display_name": "FWCI Changed (10%)",
      "field": "fwci",
      "field_type": "number",
      "test_func": not_within_10_percent,
      "test_type": "feature",
      "category": "citations",
      "description": "The <code>fwci</code> field changed by more than 10%",
    },
    {
      "display_name": "FWCI Changed (50%)",
      "field": "fwci",
      "field_type": "number",
      "test_func": not_within_50_percent,
      "test_type": "bug",
      "category": "citations",
      "description": "The <code>fwci</code> field changed by more than 50%",
    },
    # Authors
    {
      "display_name": "Authors Changed",
      "field": "authorships[*].author.id",
      "field_type": "array",
      "test_func": set_does_not_equal,
      "test_type": "bug",
      "category": "authors",
      "description": "The set of items in the <code>authorships[*].author.id</code> fields are not equal",
    },
    {
      "display_name": "Corresponding Author Changed",
      "field": "corresponding_author_ids",
      "field_type": "array",
      "test_func": set_does_not_equal,
      "test_type": "bug",
      "category": "authors",
      "description": "The set of items in the <code>corresponding_author_ids</code> fields are not equal",
    },
    # Institutions
    {
      "display_name": "Institutions Changed",
      "field": "authorships[*].institutions[*].id",
      "field_type": "array",
      "test_func": set_does_not_equal,
      "test_type": "bug",
      "category": "institutions",
      "description": "The set of items in the <code>authorships[*].institutions[*].id</code> fields are not equal",
    },
    {
      "display_name": "Country Count Increased",
      "field": "authorships[*].countries",
      "field_type": "array",
      "test_func": set_count_increased,
      "test_type": "feature",
      "category": "institutions",
      "description": "The count of the set of items in the <code>authorships[*].countries</code> fields increased",
    },
    {
      "display_name": "Country Count Decreased",
      "field": "authorships[*].countries",
      "field_type": "array",
      "test_func": set_count_decreased,
      "test_type": "bug",
      "category": "institutions",
      "description": "The count of the set of items in the <code>authorships[*].countries</code> fields decreased",
    },
    # Other
    {
      "display_name": "Title Changed",
      "field": "title",
      "field_type": "string",
      "test_func": length_not_within_5_percent,
      "test_type": "bug",
      "category": "other",
      "description": "The <code>title</code> changed more than 5% in length",
    },
    {
      "display_name": "Publication Year Changed",
      "field": "publication_year",
      "field_type": "number",
      "test_func": not_exact_match,
      "test_type": "bug",
      "category": "other",
      "description": "The <code>publication_year</code> fileds are not equal",
    },
    {
      "display_name": "Publication Date Changed",
      "field": "publication_date",
      "field_type": "date",
      "test_func": not_exact_match,
      "test_type": "bug",
      "category": "other",
      "description": "The <code>publication_date</code> fileds are not equal",
    },
    {
      "display_name": "Type Changed",
      "field": "type",
      "field_type": "string",
      "test_func": not_exact_match,
      "test_type": "bug",
      "category": "other",
      "description": "The <code>type</code> fields are not equal",
    },
    {
      "display_name": "DOI Changed",
      "field": "ids.doi",
      "field_type": "string",
      "test_func": not_exact_match,
      "test_type": "bug",
      "category": "other",
      "description": "The <code>ids.doi</code> fields are not equal",
    },
    {
      "display_name": "MAG ID Changed",
      "field": "ids.mag",
      "field_type": "string",
      "test_func": not_exact_match,
      "test_type": "bug",
      "category": "other",
      "description": "The <code>ids.mag</code> fields are not equal",
    },
    {
      "display_name": "PMID Changed",
      "field": "ids.pmid",
      "field_type": "string",
      "test_func": not_exact_match,
      "test_type": "bug",
      "category": "other",
      "description": "The <code>ids.pmid</code> fields are not equal",
    },
    {
      "display_name": "Indexed In Lost Items",
      "field": "indexed_in",
      "field_type": "array",
      "test_func": set_lost_items,
      "test_type": "bug",
      "category": "other",
      "description": "Items from the <code>indexed_in</code> field in prod were lost in walden (additions are allowed)",
    },
    {
      "display_name": "Retraction Added",
      "field": "is_retracted",
      "field_type": "boolean",
      "test_func": became_true,
      "test_type": "feature",
      "category": "other",
      "description": "The <code>is_retracted</code> field became <code>true</code>",
    },
    {
      "display_name": "Retraction Lost",
      "field": "is_retracted",
      "field_type": "boolean",
      "test_func": became_false,
      "test_type": "bug",
      "category": "other",
      "description": "The <code>is_retracted</code> field became <code>false</code>",
    },
    {
      "display_name": "Related Works Changed",
      "field": "related_works",
      "field_type": "array",
      "test_func": set_does_not_equal,
      "test_type": "bug",
      "category": "other",
      "description": "The set of items in the <code>related_works</code> fields are not equal",
    },
    {
      "display_name": "Abstract Lost",
      "field": "abstract_inverted_index",
      "field_type": "object",
      "test_func": value_lost,
      "test_type": "bug",
      "category": "other",
      "icon": "mdi-text-box-outline",
      "description": "The <code>abstract_inverted_index</code> field had a value but now is null or missing",
    },
    {
      "display_name": "Abstract Added",
      "field": "abstract_inverted_index",
      "field_type": "object",
      "test_func": value_added,
      "test_type": "feature",
      "category": "other",
      "description": "The <code>abstract_inverted_index</code> field was missing but now has a value",
    },
    {
      "display_name": "Grants Changed",
      "field": "grants",
      "field_type": "array",
      "test_func": not_exact_match,
      "test_type": "bug",
      "category": "other",
      "description": "The <code>grants</code> fields are not exactly equal",
    },
    {
      "display_name": "Grants Lost",
      "field": "grants",
      "field_type": "array",
      "test_func": value_lost,
      "test_type": "bug",
      "category": "other",
      "description": "The <code>grants</code> field had a value but now is null or missing",
    },
    {
      "display_name": "APC List Changed",
      "field": "apc_list",
      "field_type": "number",
      "test_func": not_exact_match,
      "test_type": "bug",
      "category": "other",
      "description": "The <code>apc_list</code> fields are not equal",
    },
    {
      "display_name": "APC Paid Changed",
      "field": "apc_paid",
      "field_type": "number",
      "test_func": not_exact_match,
      "test_type": "bug",
      "category": "other",
      "description": "The <code>apc_paid</code> fields are not equal",
    },
    {
      "display_name": "APC Paid USD Changed",
      "field": "apc_paid.value_usd",
      "field_type": "number",
      "test_func": not_exact_match,
      "test_type": "bug",
      "category": "other",
      "description": "The <code>apc_paid.value_usd</code> fields are not equal",
    },
    {
      "display_name": "Mesh Lost",
      "field": "mesh",
      "field_type": "array",
      "test_func": value_lost,
      "test_type": "bug",
      "category": "other",
      "description": "The <code>mesh</code> field was not null but now is null or missing",
    },
    {
      "display_name": "Mesh Added",
      "field": "mesh",
      "field_type": "array",
      "test_func": count_increased_from_zero,
      "test_type": "feature",
      "category": "other",
      "description": "The <code>mesh</code> field had zero items and now has more than zero",
    },
    {
      "display_name": "Awards Added",
      "field": "awards",
      "field_type": "array",
      "test_func": count_increased_from_null_above_zero,
      "test_type": "feature",
      "category": "other",
      "description": "The <code>awards</code> field was null or missing but now has more than zero items",
    },
    # Aboutness
    {
      "display_name": "Primary Topic Changed",
      "field": "primary_topic.id",
      "field_type": "string",
      "test_func": existing_value_changed,
      "test_type": "bug",
      "category": "aboutness",
      "description": "The <code>primary_topic.id</code> field had a value and the value changed",
    },
    {
      "display_name": "Primary Topic Added",
      "field": "primary_topic.id",
      "field_type": "string",
      "test_func": value_added,
      "test_type": "feature",
      "category": "aboutness",
      "description": "The <code>primary_topic.id</code> field was missing but now has a value",
    },
    {
      "display_name": "Keywords Lost",
      "field": "keywords",
      "field_type": "array",
      "test_func": value_lost,
      "test_type": "bug",
      "category": "aboutness",
      "description": "The <code>keywords</code> field had a value but is now null or missing",
    },
    {
      "display_name": "Keywords Added",
      "field": "keywords",
      "field_type": "array",
      "test_func": value_added,
      "test_type": "feature",
      "category": "aboutness",
      "description": "The <code>keywords</code> field was missing but now has a value",
    },
    {
      "display_name": "Concepts Changed",
      "field": "concepts[*].id",
      "field_type": "array",
      "test_func": set_does_not_equal,
      "test_type": "bug",
      "category": "aboutness",
      "description": "The set of items in the <code>concepts[*].id</code> fields are not equal",
    },
    {
      "display_name": "Concepts Lost",
      "field": "concepts",
      "field_type": "array",
      "test_func": value_lost,
      "test_type": "bug",
      "category": "aboutness",
      "description": "The <code>concepts</code> field had a value but is now null or missing",
    },
    {
      "display_name": "SDGs Changed",
      "field": "sustainable_development_goals[*].id",
      "field_type": "array",
      "test_func": set_does_not_equal,
      "test_type": "bug",
      "category": "aboutness",
      "description": "The set of items in the <code>sustainable_development_goals[*].id</code> fields are not equal",
    },
    {
      "display_name": "SDGs Lost",
      "field": "sustainable_development_goals",
      "field_type": "array",
      "test_func": value_lost,
      "test_type": "bug",
      "category": "aboutness",
      "description": "The <code>sustainable_development_goals</code> field had a value but is now null or missing",
    },
  ],
  "sources": [
    {
      "display_name": "is_oa Added",
      "field": "is_oa",
      "field_type": "boolean",
      "test_func": became_true,
      "test_type": "feature",
      "category": "works",
      "description": "The <code>is_oa</code> field became true",
    },
    {
      "display_name": "Type Changed to Repository",
      "field": "type",
      "field_type": "string",
      "test_func": type_changed_to_repository,
      "test_type": "feature",
      "category": "works",
      "description": "The <code>type</code> field changed to <code>repository</code>",
    },
    {
      "display_name": "Host Organization Lost",
      "field": "host_organization",
      "field_type": "string",
      "test_func": value_lost,
      "test_type": "feature",
      "category": "works",
      "description": "The <code>host_organization</code> field had a value but is now null or missing",
    },
  ],
  "institutions": [
    {
      "display_name": "Type Changed from Funder",
      "field": "type",
      "field_type": "boolean",
      "test_func": type_changed_from_funder,
      "test_type": "feature",
      "category": "works",
      "description": "The <code>type</code> field changed away from <code>funder</code>",
    },  
  ],
  "publishers": [ 
  ]
}

entities = [
  'authors',
  'awards',
  'continents', 
  'countries',
  'concepts',
  'domains', 
  'fields', 
  'funders', 
  'institution-types', 
  'institutions', 
  'keywords', 
  'languages', 
  'licenses', 
  'publishers', 
  'sdgs', 
  'source-types', 
  'sources', 
  'subfields', 
  'topics', 
  'work-types', 
  'works'
]

non_works_tests = [
  {
    "display_name": "Works Count Decreased (5%)",
    "field": "works_count",
    "field_type": "number",
    "test_func": below_5_percent,
    "test_type": "bug",
    "category": "works",
    "icon": "mdi-file-document-outline",
    "description": "The <code>works_count</code> field decreased by 5% or more",
  },
  {
    "display_name": "Works Count Increased (5%)",
    "field": "works_count",
    "field_type": "number",
    "test_func": above_5_percent,
    "test_type": "feature",
    "category": "works",
    "icon": "mdi-file-document-outline",
    "description": "The <code>works_count</code> field increased by 5% or more",
  },
  {
    "display_name": "Citation Count Decreased (5%)",
    "field": "cited_by_count",
    "field_type": "number",
    "test_func": below_5_percent,
    "test_type": "bug",
    "category": "citations",
    "icon": "mdi-file-document-outline",
    "description": "The <code>cited_by_count</code> field decreased by 5% or more",
  },
    {
    "display_name": "Citation Count Increased (5%)",
    "field": "cited_by_count",
    "field_type": "number",
    "test_func": above_5_percent,
    "test_type": "feature",
    "category": "citations",
    "icon": "mdi-file-document-outline",
    "description": "The <code>cited_by_count</code> field increased by 5% or more",
  }
]

def make_tests_schema():
  schema = {}
  for entity in entities:
    if entity in tests_schema_base:
      schema[entity] = tests_schema_base[entity]
    else:
      schema[entity] = []
    if entity != "works":
      schema[entity].extend(non_works_tests)

  return schema

tests_schema = make_tests_schema()

last_week_samples_schema = {
  "works": {"both": 10000, "walden": 500, "prod": 500},
  #"sources": {"both": 10000, "walden": 500, "prod": 500},
  #"institutions": {"both": 10000, "walden": 500, "prod": 500},
  #"publishers": {"both": 500, "walden": 500, "prod": 500},
}
