from datetime import date
from decimal import Decimal
from enum import Enum
from typing import ClassVar, Optional

from typing_extensions import Self

from sdif.fields import FieldType
from sdif.model_meta import model, spec
from sdif.time import Time
from sdif.time import TimeCode as TimeCode
from sdif.time import TimeT

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

    short_meters_hytek_nonstandard = "S"

    def normalize(self) -> Self:
        return {
            self.short_meters_int: self.short_meters,
            self.long_meters_int: self.long_meters,
            self.short_yards_int: self.short_yards,
            self.short_meters_hytek_nonstandard: self.short_meters,
        }.get(self, self)


class EventTimeClassCode(Enum):
    """EVENT TIME CLASS Code 014: Event Time Class code
    The following characters are concatenated to form a 2-byte
    code for the event time class.  The first character
    indicates the lower limit; the second character indicates
    the upper limit.  22 indicates B meets, 23 indicates B-A
    meets, and 4O indicates AA+ meets.
    """

    no_lower_limit = "U"
    no_upper_limit = "0"
    novice = "1"
    b_standard = "2"
    bb_standard = "P"
    a_standard = "3"
    aa_standard = "4"
    aaa_standard = "5"
    aaaa_standard = "6"
    junior_standard = "J"
    senior_standard = "S"


class AttachCode(Enum):
    """ATTACH Code 016: Attached code"""

    attached = "A"
    unattached = "U"


class OrderCode(Enum):
    """ORDER Code 024: relay leg order"""

    not_on_team = "0"
    first_leg = "1"
    second_leg = "2"
    third_leg = "3"
    fourth_leg = "4"
    alternate = "A"


class EthnicityCode(Enum):
    """ETHNICITY Code 026
    The first byte contains the first ethnicity selection.
    The second byte contains an optional second ethnicity
    selection.
    If the first byte contains a V,W or X then the second
    byte must be blank.
    [Ed. note: X is not defined in the v3 spec.]
    """

    african_american = "Q"
    asian_pacific_islander = "R"
    caucasian = "S"
    hispanic = "T"
    native_american = "U"
    other = "V"
    decline = "W"


# Records


@model(frozen=True, kw_only=True)
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


@model(frozen=True, kw_only=True)
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
    meet_address_1: Optional[str] = spec(42, 22)
    meet_address_2: Optional[str] = spec(64, 22)
    meet_city: Optional[str] = spec(86, 20, m2=True)
    meet_state: Optional[str] = spec(106, 2, type=t.usps, m2=True)
    postal_code: Optional[str] = spec(108, 10)
    country: Optional[str] = spec(118, 3)
    meet: Optional[MeetTypeCode] = spec(121, 1, m2=True)
    meet_start: date = spec(122, 8)
    meet_end: Optional[date] = spec(130, 8, m2=True)
    pool_altitude_ft: Optional[int] = spec(138, 4)
    course: Optional[CourseStatusCode] = spec(150, 1)


@model(frozen=True, kw_only=True)
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


@model(frozen=True, kw_only=True)
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


@model(frozen=True, kw_only=True)
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
    seed_time: Optional[Time] = spec(89, 8)
    seed_time_course: Optional[CourseStatusCode] = spec(97, 1)
    prelim_time: Optional[TimeT] = spec(98, 8, t.time)
    prelim_time_course: Optional[CourseStatusCode] = spec(106, 1)
    swim_off_time: Optional[TimeT] = spec(107, 8, t.time)
    swim_off_time_course: Optional[CourseStatusCode] = spec(115, 1)
    finals_time: Optional[TimeT] = spec(116, 8, t.time)
    finals_time_course: Optional[CourseStatusCode] = spec(124, 1)
    prelim_heat_number: Optional[int] = spec(125, 2)
    prelim_lane_number: Optional[int] = spec(127, 2)
    finals_heat_number: Optional[int] = spec(129, 2)
    finals_lane_number: Optional[int] = spec(131, 2)
    prelim_place_ranking: Optional[int] = spec(133, 3)
    finals_place_ranking: Optional[int] = spec(136, 3)
    points_scored_finals: Optional[Decimal] = spec(139, 4)
    event_time_class: Optional[str] = spec(143, 2)
    flight_status: Optional[str] = spec(145, 1)


@model(frozen=True, kw_only=True)
class IndividualInfo:
    """Contains additional information that is not
    included in pre version 3 SDI formats.

    This record provides space for the new USS# as well as the
    swimmers preferred first name. For meet files this record will
    follow the D0 record and the F0 record if relays are included.
    A swimmer with multiple D0 records will have one D3 record
    following his/her first D0 record.
    """

    identifier: ClassVar[str] = "D3"
    uss_number: Optional[str] = spec(3, 14, t.ussnum, m2=True)
    preferred_first_name: Optional[str] = spec(17, 15)
    ethnicity_1: Optional[EthnicityCode] = spec(32, 1)
    ethnicity_2: Optional[EthnicityCode] = spec(33, 1)
    junior_high: Optional[bool] = spec(34, 1)
    senior_high: Optional[bool] = spec(35, 1)
    ymca_ywca: Optional[bool] = spec(36, 1)
    college: Optional[bool] = spec(37, 1)
    summer_league: Optional[bool] = spec(38, 1)
    masters: Optional[bool] = spec(39, 1)
    disabled_sports_org: Optional[bool] = spec(40, 1)
    water_polo: Optional[bool] = spec(41, 1)
    none: Optional[bool] = spec(42, 1)


@model(frozen=True, kw_only=True)
class RelayEvent:
    """Identify the relay team by name, USS team code,
    and gender.  Identify the stroke, distance, event
    number, date and time of the swims.

    This record is used to identify the team and the relay event.
    When used, one relay event record would be submitted for each
    relay squad entered in a relay event.  The relay team name, USS
    team code, and gender code are required.  Fields for the stroke,
    distance, event number, age range, and date of swim, are also
    required.  Additional fields provide for the age or class, seed
    time, prelim time, swim off time, finals time, and pool lanes
    used in competition.

    relay_team_name is one alpha char to
    concatenate with the abbreviated team
    name (48/16) in record C1 -- creates such
    names as "Dolphins A"
    """

    identifier: ClassVar[str] = "E0"
    organization: Optional[OrganizationCode] = spec(3, 1, m2=True)
    relay_team_name: str = spec(12, 1)
    team_code: str = spec(13, 6)
    n_f0_records: Optional[int] = spec(19, 2)
    event_sex: EventSexCode = spec(21, 1)
    relay_distance: int = spec(22, 4)
    stroke: StrokeCode = spec(26, 1)
    event_number: Optional[str] = spec(27, 4)
    event_age: str = spec(31, 4)
    total_athlete_age: int = spec(35, 3)
    swim_date: Optional[date] = spec(38, 8)
    seed_time: Optional[TimeT] = spec(46, 8)
    seed_course: Optional[CourseStatusCode] = spec(54, 1)
    prelim_time: Optional[TimeT] = spec(55, 8)
    prelim_course: Optional[CourseStatusCode] = spec(63, 1)
    swimoff_time: Optional[TimeT] = spec(64, 8)
    swimoff_course: Optional[CourseStatusCode] = spec(72, 1)
    finals_time: Optional[TimeT] = spec(73, 8)
    finals_course: Optional[CourseStatusCode] = spec(81, 1)
    prelim_heat: Optional[int] = spec(82, 2)
    prelim_lane: Optional[int] = spec(84, 2)
    finals_heat: Optional[int] = spec(86, 2)
    finals_lane: Optional[int] = spec(88, 2)
    prelim_place: Optional[int] = spec(90, 3)
    finals_place: Optional[int] = spec(93, 3)
    finals_points: Optional[Decimal] = spec(96, 4)
    event_time_class_lower: Optional[EventTimeClassCode] = spec(100, 1)
    event_time_class_upper: Optional[EventTimeClassCode] = spec(101, 1)


@model(frozen=True, kw_only=True)
class RelayName:
    """Identify the athletes on a relay team by name, USS
    registration number, birth date and gender.
    Identify the stroke, distance, event number, date,
    session and time of the swims.

    This record is used to identify the athletes on a relay team and
    the relay order.  When used, one relay name record is submitted
    for each relay athlete entered in a relay event.  Alternates may
    be listed on additional records as an optional method of using
    this record.  The relay team name, USS team code, and gender
    code are required.  The Event ID # field (12/4) is required to
    properly identify the relay team to an event and to further link
    the splits for a relay athlete.  Fields for the stroke, distance,
    event number, age or class, and date of swim, are also required.
    Additional fields provide for the seed time, prelim time, swim
    off time, finals time, and pool lanes used in competition.

    NOTE:  Relay name records must be preceded by at least one E0
    relay event record.  If this record is missing, the athlete on a
    relay team cannot be attached to the proper relay squad.


    relay_team_name:  one alpha char to concatenate with the team abbreviation in
    record C1 -- creates such names as "Dolphins A"
    """

    identifier: ClassVar[str] = "F0"
    organization: Optional[OrganizationCode] = spec(3, 1, m2=True)
    team_code: str = spec(16, 6)
    relay_team_name: Optional[str] = spec(22, 1)
    swimmer_name: str = spec(23, 28, t.name_)
    uss_number: Optional[str] = spec(51, 12)
    citizen: Optional[str] = spec(63, 3)
    birthdate: Optional[date] = spec(66, 8, m2=True)
    age_or_class: Optional[str] = spec(74, 2)
    sex: SexCode = spec(76, 1)
    prelim_order: OrderCode = spec(77, 1)
    swimoff_order: OrderCode = spec(78, 1)
    finals_order: OrderCode = spec(79, 1)
    leg_time: Optional[TimeT] = spec(80, 8)
    course: Optional[CourseStatusCode] = spec(88, 1)
    takeoff_time: Optional[Decimal] = spec(89, 4)
    uss_number_new: Optional[str] = spec(93, 14, t.ussnum, m2=True)
    preferred_first_name: Optional[str] = spec(107, 15)


@model(frozen=True, kw_only=True)
class FileTerminator:
    """Identify the logical end of file for a file
    transmission.  Record statistics and swim
    statistics are listed for convenience.

    This record is mandatory in each file.  Each file ends with this
    record and each file has only one record of this type.  The first
    four fields are mandatory.  Additional fields provide for text
    and record counts.
    """

    identifier: ClassVar[str] = "Z0"
    organization: Optional[OrganizationCode] = spec(3, 1, m2=True)
    file_code: FileCode = spec(12, 2)
    notes: str = spec(14, 30)
    n_b_records: Optional[int] = spec(44, 3)
    n_meets: Optional[int] = spec(47, 3)
    n_c_records: Optional[int] = spec(50, 4)
    n_teams: Optional[int] = spec(54, 4)
    n_d_records: Optional[int] = spec(58, 6)
    n_swimmers: Optional[int] = spec(64, 6)
    n_e_records: Optional[int] = spec(70, 5)
    n_f_records: Optional[int] = spec(75, 6)
    n_g_records: Optional[int] = spec(81, 6)
    batch_number: Optional[int] = spec(87, 5)
    n_new_members: Optional[int] = spec(92, 3)
    n_renew_members: Optional[int] = spec(95, 3)
    n_member_changes: Optional[int] = spec(98, 3)
    n_member_deletes: Optional[int] = spec(101, 3)
