from __future__ import annotations

from datetime import date
from decimal import Decimal
from enum import Enum
from typing import ClassVar, Optional

from sdif.fields import FieldType, model, spec

t = FieldType


# Code tables
class OrganizationCode(Enum):
    """ORG Code 001: Organization code"""

    uss = "1"
    masters = "2"
    ncaa = "3"
    ncaa_div_i = "4"
    ncaa_div_ii = "5"
    ncaa_div_iii = "6"
    ymca = "7"
    fina = "8"
    high_school = "9"


class FileCode(Enum):
    """FILE Code 003: File/Transmission Type code"""

    meet_registrations = "01"
    meet_results = "02"
    ovc = "03"
    national_age_group_record = "04"
    lsc_age_group_record = "05"
    lsc_motivational_list = "06"
    national_records_and_rankings = "07"
    team_selection = "08"
    lsc_best_times = "09"
    uss_registration = "10"
    top_16 = "16"
    vendor_defined = "20"


class MeetTypeCode(Enum):
    """MEET Code 005: Meet Type code"""

    invitational = "1"
    regional = "2"
    lsc_championship = "3"
    zone = "4"
    zone_championship = "5"
    national_championship = "6"
    juniors = "7"
    seniors = "8"
    dual = "9"
    time_trials = "0"
    international = "A"
    open = "B"
    league = "C"


class SexCode(Enum):
    """SEX Code 010: Swimmer Sex code
    https://medium.com/gender-2-0/falsehoods-programmers-believe-about-gender-f9a3512b4c9c
    """

    male = "M"
    female = "F"


class EventSexCode(Enum):
    """EVENT SEX Code 011: Sex of Event code"""

    male = "M"
    female = "F"
    mixed = "X"


class StrokeCode(Enum):
    """STROKE Code 012: Event Stroke code"""

    freestyle = "1"
    backstroke = "2"
    breaststroke = "3"
    butterfly = "4"
    im = "5"
    free_relay = "6"
    medley_relay = "7"


class CourseStatusCode(Enum):
    """COURSE Code 013: Course/Status code
    Please note that there are alternatives for the three types
    of pools.  The alpha characters make the file more readable.
    Either may be used.
    """

    short_meters_int = "1"
    short_meters = "M"
    short_yards_int = "2"
    short_yards = "Y"
    long_meters_int = "3"
    long_meters = "L"
    disqualified = "X"

    def normalize(self) -> CourseStatusCode:
        return {
            self.short_meters_int: self.short_meters,
            self.long_meters_int: self.long_meters,
            self.short_yards_int: self.short_yards,
        }.get(self, self)


class AttachCode(Enum):
    """ATTACH Code 016: Attached code"""

    attached = "A"
    unattached = "U"


# Records


@model(frozen=True)
class FileDescription:
    """Identify the file and the type of data to be
    transmitted.  Contact person and phone number
    included to assist with use of information on the
    file.

    This record is mandatory for each transfer of data within this
    file structure.  Each file begins with this record and each file
    has only one record of this type.
    """

    identifier: ClassVar[str] = "A0"
    organization: Optional[OrganizationCode] = spec(start=3, len=1, m2=True)
    sdif_version: Optional[str] = spec(4, 8)
    file_code: FileCode = spec(12, 2)
    software_name: Optional[str] = spec(44, 20)
    software_version: Optional[str] = spec(64, 10)
    contact_name: str = spec(74, 20)
    contact_phone: str = spec(94, 12, type=t.phone)
    file_creation: date = spec(start=106, len=8)
    submitted_by_lsc: Optional[str] = spec(start=156, len=2)


@model(frozen=True)
class Meet:
    """Identify the meet name, address, and dates.

    This record is used to identify the meet name and address.  The
    meet name is required, plus the city, state, meet type, start
    and end dates.  Additional fields provide for the street address,
    postal code and country code.  Each file may only have one
    record of this type.
    """

    identifier: ClassVar[str] = "B1"
    organization: Optional[OrganizationCode] = spec(3, 1)
    meet_name: str = spec(12, 30)
    meet_address_1: str = spec(42, 22)
    meet_address_2: str = spec(64, 22)
    meet_city: Optional[str] = spec(86, 20, m2=True)
    meet_state: Optional[str] = spec(106, 2, type=t.usps, m2=True)
    postal_code: Optional[str] = spec(108, 10)
    country: Optional[str] = spec(118, 3)
    meet: Optional[MeetTypeCode] = spec(121, 1, m2=True)
    meet_start: date = spec(122, 8)
    meet_end: Optional[date] = spec(130, 8, m2=True)
    pool_altitude_ft: Optional[int] = spec(138, 4)
    course: Optional[CourseStatusCode] = spec(150, 1)


@model(frozen=True)
class TeamId:
    """Identify the team name, code and address.  Region
    code defines USS region for team.

    This record is used to identify the team name, team code, plus
    region.  When used, more than one team record can be transmitted
    for a single meet.  The team name, USS team code and team
    abbreviation are required.  The USS region code is also required.
    Additional fields provide for the street address, city, state,
    postal code, and country code.
    """

    identifier: ClassVar[str] = "C1"
    organization: Optional[OrganizationCode] = spec(3, 1)
    team_code: str = spec(12, 6)
    name: str = spec(18, 30)
    abbreviation: Optional[str] = spec(48, 16)
    address_1: Optional[str] = spec(64, 22)
    address_2: Optional[str] = spec(86, 22)
    city: Optional[str] = spec(108, 20)
    state: Optional[str] = spec(128, 2, t.usps)
    postal_code: Optional[str] = spec(130, 10, t.postal_code)
    country: Optional[str] = spec(140, 3)
    region: Optional[str] = spec(143, 1)
    team_code5: Optional[str] = spec(150, 1)


@model(frozen=True)
class TeamEntry:
    """Identify the team coach and the number of entries
    for the team.

    This record is used to identify the team coach.  When used, one
    team entry record would be submitted with the C1 team ID record.
    The USS team code and team coach field are required.  Additional
    fields provide for the number of individual swimmers, number of
    splash records, number of relay entries, number of relay name
    entries and number of split records.
    """

    identifier: ClassVar[str] = "C2"
    organization: Optional[OrganizationCode] = spec(3, 1, m2=True)
    team_code: Optional[str] = spec(12, 6, m2=True)
    coach_name: Optional[str] = spec(18, 30, m2=True)
    coach_phone: Optional[str] = spec(48, 12, t.phone)
    n_entries: Optional[int] = spec(60, 6)
    n_athletes: Optional[int] = spec(66, 6)
    n_relay_entries: Optional[int] = spec(72, 5)
    n_split_records: Optional[int] = spec(83, 6)
    short_name: Optional[str] = spec(89, 16)
    team_code5: Optional[str] = spec(150, 1)


@model(frozen=True)
class IndividualEvent:
    """Identify the athlete by name, registration number,
    birth date and gender.  Identify the stroke,
    distance, event number and time of the swims.

    This record is used to identify the athlete and the individual
    event.  When used, one individual event record would be
    submitted for each swimmer entered in an individual event.  The
    athlete name, USS registration number, birth date and gender
    code are required.  Fields for the stroke, distance, event
    number, age range, and date of swim are also required.
    Additional fields provide for the citizenship, age or class,
    seed time, prelim time, swim off time, finals time and pool
    lanes used in competition.

    Note on event_age:
        first two bytes are lower age limit (digits, or "UN" for no limit)
        last two bytes are upper age limit (digits, or "OV" for no limit)
        if the age is only one digit, fill with a zero (no blanks allowed)

    Event age, event sex code, event distance, and stroke code are mandatory
    except for relay-only swimmers.
    """

    identifier: ClassVar[str] = "D0"
    organization: Optional[OrganizationCode] = spec(3, 1)
    name: str = spec(12, 28, t.name_)
    ussn: Optional[str] = spec(40, 12, m2=True)
    attached: Optional[AttachCode] = spec(52, 1)
    citizen: Optional[str] = spec(53, 3)
    birthdate: Optional[date] = spec(56, 8, m2=True)
    age_or_class: Optional[str] = spec(64, 2)
    sex: SexCode = spec(66, 1)
    event_sex: Optional[EventSexCode] = spec(67, 1)
    event_distance: Optional[int] = spec(68, 4)
    stroke: Optional[StrokeCode] = spec(72, 1)
    event_number: Optional[str] = spec(73, 4)
    event_age: Optional[str] = spec(77, 4)
    date_of_swim: Optional[date] = spec(81, 8)
    seed_time: Optional[str] = spec(89, 8, t.time)
    seed_time_course: Optional[CourseStatusCode] = spec(97, 1)
    prelim_time: Optional[str] = spec(98, 8, t.time)
    prelim_time_course: Optional[CourseStatusCode] = spec(106, 1)
    swim_off_time: Optional[str] = spec(107, 8, t.time)
    swim_off_time_course: Optional[CourseStatusCode] = spec(115, 1)
    finals_time: Optional[str] = spec(116, 8, t.time)
    finals_time_course: Optional[CourseStatusCode] = spec(124, 1)
    prelim_heat_number: Optional[int] = spec(125, 2)
    prelim_lane_number: Optional[int] = spec(127, 2)
    finals_heat_number: Optional[int] = spec(129, 2)
    finals_lane_number: Optional[int] = spec(131, 2)
    prelim_place_ranking: Optional[int] = spec(133, 3)
    finals_place_ranking: Optional[int] = spec(136, 3)
    points_scored_finals: Optional[Decimal] = spec(139, 4)
    event_time_class: Optional[str] = spec(143, 2)
    flight_status: str = spec(145, 1)
