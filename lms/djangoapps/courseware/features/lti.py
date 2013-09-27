#pylint: disable=C0111

from django.contrib.auth.models import User
from lettuce import world, step
from lettuce.django import django_url
from common import course_id

from student.models import CourseEnrollment


@step('I view the LTI and error is shown$')
def lti_is_not_rendered(_step):
    # error is shown
    assert world.is_css_present('.error_message')

    # iframe is not presented
    assert not world.is_css_present('iframe')

    # link is not presented
    assert not world.is_css_present('.link_lti_new_window')


@step('I view the LTI and it is rendered in (.*)$')
def lti_is_rendered(_step, rendered_in):
    if rendered_in.stip() == 'iframe':
        assert world.is_css_present('iframe')
        assert not world.is_css_present('.link_lti_new_window')
        assert not world.is_css_present('.error_message')

        #inside iframe test content is presented
        with world.browser.get_iframe('ltiLaunchFrame') as iframe:
            # iframe does not contain functions from terrain/ui_helpers.py
            assert iframe.is_element_present_by_css('.result', wait_time=5)
            assert ("This is LTI tool. Success." == world.retry_on_exception(
                lambda: iframe.find_by_css('.result')[0].text,
                max_attempts=5
            ))

    elif rendered_in.stip() == 'new page':
        assert not world.is_css_present('iframe')
        assert world.is_css_present('.link_lti_new_window')
        assert not world.is_css_present('.error_message')
        # TODO, follow target = _blank here
    else:  # incorrent rendered_in parametetr
        assert False


@step('I view the LTI but incorrect_signature warning is rendered$')
def incorrect_lti_is_rendered(_step):
    assert world.is_css_present('iframe')
    assert not world.is_css_present('.link_lti_new_window')
    assert not world.is_css_present('.error_message')
    #inside iframe test content is presented
    with world.browser.get_iframe('ltiLaunchFrame') as iframe:
        # iframe does not contain functions from terrain/ui_helpers.py
        assert iframe.is_element_present_by_css('.result', wait_time=5)
        assert ("Wrong LTI signature" == world.retry_on_exception(
            lambda: iframe.find_by_css('.result')[0].text,
            max_attempts=5
        ))


@step('the course has correct LTI credentials$')
def set_correct_lti_passport(_step):
    coursenum = 'test_course'
    metadata = {
        'lti_passports': ["correct_lti_id:{}:{}".format(
            world.lti_server.oauth_settings['client_key'],
            world.lti_server.oauth_settings['client_secret']
        )]
    }
    i_am_registered_for_the_course(coursenum, metadata)


@step('the course has incorrect LTI credentials$')
def set_incorrect_lti_passport(_step):
    coursenum = 'test_course'
    metadata = {
        'lti_passports': ["test_lti_id:{}:{}".format(
            world.lti_server.oauth_settings['client_key'],
            "incorrect_lti_secret_key"
        )]
    }
    i_am_registered_for_the_course(coursenum, metadata)


@step('the course has an LTI component with(.*)correct fields, new_page is(.*)$')
def add_incorrect_lti_to_course(_step, incorrect, new_page):
    category = 'lti'

    if incorrect.strip():  # incorrect fields
        lti_id = 'incorrect_lti_id'
    else:  # correct fields
        lti_id = 'correct_lti_id'

    if new_page.strip().lower() == 'false':
        new_page = False
    else:  # default is True
        new_page = True

    world.ItemFactory.create(
        parent_location=world.scenario_dict['SEQUENTIAL'].location,
        category=category,
        display_name='LTI',
        metadata={
            'lti_id': lti_id,
            'launch_url': world.lti_server.oauth_settings['lti_base'] + world.lti_server.oauth_settings['lti_endpoint'],
            'new_page': new_page
        }
    )
    course = world.scenario_dict["COURSE"]
    chapter_name = world.scenario_dict['SECTION'].display_name.replace(
        " ", "_")
    section_name = chapter_name
    path = "/courses/{org}/{num}/{name}/courseware/{chapter}/{section}".format(
        org=course.org,
        num=course.number,
        name=course.display_name.replace(' ', '_'),
        chapter=chapter_name,
        section=section_name)
    url = django_url(path)

    world.browser.visit(url)


def create_course(course, metadata):

    # First clear the modulestore so we don't try to recreate
    # the same course twice
    # This also ensures that the necessary templates are loaded
    world.clear_courses()

    # Create the course
    # We always use the same org and display name,
    # but vary the course identifier (e.g. 600x or 191x)
    world.scenario_dict['COURSE'] = world.CourseFactory.create(
        org='edx',
        number=course,
        display_name='Test Course',
        metadata=metadata
    )

    # Add a section to the course to contain problems
    world.scenario_dict['SECTION'] = world.ItemFactory.create(
        parent_location=world.scenario_dict['COURSE'].location,
        display_name='Test Section'
    )
    world.scenario_dict['SEQUENTIAL'] = world.ItemFactory.create(
        parent_location=world.scenario_dict['SECTION'].location,
        category='sequential',
        display_name='Test Section')


def i_am_registered_for_the_course(course, metadata):
    # Create the course
    create_course(course, metadata)

    # Create the user
    world.create_user('robot', 'test')
    usr = User.objects.get(username='robot')

    # If the user is not already enrolled, enroll the user.
    CourseEnrollment.enroll(usr, course_id(course))

    world.log_in(username='robot', password='test')
