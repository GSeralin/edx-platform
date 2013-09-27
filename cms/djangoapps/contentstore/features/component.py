#pylint: disable=C0111
#pylint: disable=W0621

from lettuce import world, step
from nose.tools import assert_true, assert_in, assert_equal  # pylint: disable=E0611

DATA_LOCATION = 'i4x://edx/templates'


@step(u'I am editing a new unit$')
def add_unit(step):
    css_selectors = ['a.new-courseware-section-button', 'input.new-section-name-save', 'a.new-subsection-item',
                    'input.new-subsection-name-save', 'div.section-item a.expand-collapse-icon', 'a.new-unit-item']
    for selector in css_selectors:
        world.css_click(selector)


@step(u'I add this type of single step component:$')
def add_a_single_step_component(step):
    for component in [step_hash['Component'] for step_hash in step.hashes]:
        assert_in(component, ['Discussion', 'Video'])
        css_selector = 'a[data-type="{}"]'.format(component.lower())
        world.css_click(css_selector)


@step(u'I see this type of single step component:$')
def see_a_single_step_component(step):
    for component in [step_hash['Component'] for step_hash in step.hashes]:
        assert_in(component, ['Discussion', 'Video'])
        component_css = 'section.xmodule_{}Module'.format(component)
        assert_true(world.is_css_present(component_css),
                    "{} couldn't be found".format(component))


@step(u'I add this type of( Advanced)? (HTML|Problem) component:$')
def add_a_multi_step_component(step, is_advanced, category):
    category = category.lower()
    # from nose.tools import set_trace; set_trace()
    for step_hash in step.hashes:
        css_selector = 'a[data-type="{}"]'.format(category)
        world.css_click(css_selector)

        if is_advanced:
            css = 'ul.problem-type-tabs a[href="#tab2"]'
            world.css_click(css)

        # This will find the links for the given category
        span_css = 'div.new-component-templates a[data-category="{}"] span.name'.format(category)
        links = world.css_find(span_css)

        # Assuming there is one and only one link with that exact text.
        # If not the test will fail on the next step anyhow.
        assert step_hash['Component'] in [link.text for link in links]
        for link in links:
            if link.text == step_hash['Component']:
                link.click()
                break


@step(u'I see (HTML|Problem) components in this order:')
def see_a_multi_step_component(step, category):
    components = world.css_find('li.component section.xmodule_display')
    for idx, step_hash in enumerate(step.hashes):

        # Blank text is trickier to match
        if category == 'HTML':
            if step_hash['Component'] == 'Text':
                assert_equal(u'\n    \n', components[idx].html)
            else:
                html_matcher = {
                    'Announcement':
                        '<p> Words of encouragement! This is a short note that most students will read. </p>',
                    'E-text Written in LaTeX':
                        '<h2>Example: E-text page</h2>',
                }
                html_to_match = html_matcher[step_hash['Component']]
                assert_in(html_to_match, components[idx].html)
        else:
            assert_in(step_hash['Component'].upper(), components[idx].text)


@step(u'I add the following components:')
def add_components(step):
    for component in [step_hash['Component'] for step_hash in step.hashes]:
        assert component in COMPONENT_DICTIONARY
        for css in COMPONENT_DICTIONARY[component]['steps']:
            world.css_click(css)


@step(u'I see the following components')
def check_components(step):
    for component in [step_hash['Component'] for step_hash in step.hashes]:
        assert component in COMPONENT_DICTIONARY
        assert_true(COMPONENT_DICTIONARY[component]['found_func'](),
            "{} couldn't be found".format(component))


@step(u'I delete all components')
def delete_all_components(step):
    for _ in range(len(COMPONENT_DICTIONARY)):
        world.css_click('a.delete-button')


@step(u'I see no components')
def see_no_components(steps):
    assert world.is_css_not_present('li.component')


@step(u'I delete a component')
def delete_one_component(step):
    world.css_click('a.delete-button')


@step(u'I edit and save a component')
def edit_and_save_component(step):
    world.css_click('.edit-button')
    world.css_click('.save-button')


def step_selector_list(data_type, path, index=1):
    selector_list = ['a[data-type="{}"]'.format(data_type)]
    if index != 1:
        selector_list.append('a[id="ui-id-{}"]'.format(index))
    if path is not None:
        selector_list.append('a[data-location="{}/{}/{}"]'.format(DATA_LOCATION, data_type, path))
    return selector_list


def found_text_func(text):
    return lambda: world.browser.is_text_present(text)


def found_css_func(css):
    return lambda: world.is_css_present(css, wait_time=2)


COMPONENT_TYPE = {
    'Discussion': {
        'steps': step_selector_list('discussion', None),
        'found_func': found_css_func('section.xmodule_DiscussionModule')
    },
    'HTML': {
        'steps': step_selector_list('html', 'Blank_HTML_Page'),
        #this one is a blank html so a more refined search is being done
        'found_func': lambda: '\n    \n' in [x.html for x in world.css_find('section.xmodule_HtmlModule')]
    },
    'Problem': {
        'steps': step_selector_list('problem', 'Blank_Common_Problem'),
        'found_func': found_text_func('BLANK COMMON PROBLEM')
    },
    'Video': {
        'steps': step_selector_list('video', None),
        'found_func': found_css_func('section.xmodule_VideoModule')
    }
}



    # 'Problem': {
    #     'Blank Common Problem': u'<h2 class="problem-header">\n  Blank Common Problem\n</h2>',
    #     'Dropdown': '<h2 class="problem-header">\n  Dropdown\n</h2>',
    #     'Multiple Choice': '<h2 class="problem-header">\n  Multiple Choice\n</h2>',
    #     'Numerical Input': '<h2 class="problem-header">\n  Numerical Input\n</h2>',
    #     'Text Input': '<h2 class="problem-header">\n  Text Input\n</h2>',
    #     'Blank Advanced Problem': '<h2 class="problem-header">\n  Blank Advanced Problem\n</h2>',
    #     'Circuit Schematic Builder': '<h2 class="problem-header">\n  Circuit Schematic Builder\n</h2>',
    #     'Custom Python-Evaluated Input': '<h2 class="problem-header">\n  Custom Python-Evaluated Input\n</h2>',
    #     'Drag and Drop': '<h2 class="problem-header">\n  Drag and Drop\n</h2>',
    #     'Image Mapped Input': '<h2 class="problem-header">\n  Image Mapped Input\n</h2>',
    #     'Math Expression Input': '<h2 class="problem-header">\n  Math Expression Input\n</h2>',
    #     'Problem Written in LaTeX': '<h2 class="problem-header">\n  Problem Written in LaTeX\n</h2>',
    #     'Problem with Adaptive Hint': '<h2 class="problem-header">\n  Problem with Adaptive Hint\n</h2>',
    # },}

COMPONENT_DICT = {
    'Blank HTML': {
        'steps': step_selector_list('html', 'Blank_HTML_Page'),
        #this one is a blank html so a more refined search is being done
        'found_func': lambda: '\n    \n' in [x.html for x in world.css_find('section.xmodule_HtmlModule')]
    },
    'LaTex': {
        'steps': step_selector_list('html', 'E-text_Written_in_LaTeX'),
        'found_func': found_text_func('EXAMPLE: E-TEXT PAGE')
    },
    'Blank Problem': {
        'steps': step_selector_list('problem', 'Blank_Common_Problem'),
        'found_func': found_text_func('BLANK COMMON PROBLEM')
    },
    'Dropdown': {
        'steps': step_selector_list('problem', 'Dropdown'),
        'found_func': found_text_func('DROPDOWN')
    },
    'Multi Choice': {
        'steps': step_selector_list('problem', 'Multiple_Choice'),
        'found_func': found_text_func('MULTIPLE CHOICE')
    },
    'Numerical': {
        'steps': step_selector_list('problem', 'Numerical_Input'),
        'found_func': found_text_func('NUMERICAL INPUT')
    },
    'Text Input': {
        'steps': step_selector_list('problem', 'Text_Input'),
        'found_func': found_text_func('TEXT INPUT')
    },
    'Advanced': {
        'steps': step_selector_list('problem', 'Blank_Advanced_Problem', index=2),
        'found_func': found_text_func('BLANK ADVANCED PROBLEM')
    },
    'Circuit': {
        'steps': step_selector_list('problem', 'Circuit_Schematic_Builder', index=2),
        'found_func': found_text_func('CIRCUIT SCHEMATIC BUILDER')
    },
    'Custom Python': {
        'steps': step_selector_list('problem', 'Custom_Python-Evaluated_Input', index=2),
        'found_func': found_text_func('CUSTOM PYTHON-EVALUATED INPUT')
    },
    'Image Mapped': {
        'steps': step_selector_list('problem', 'Image_Mapped_Input', index=2),
        'found_func': found_text_func('IMAGE MAPPED INPUT')
    },
    'Math Input': {
        'steps': step_selector_list('problem', 'Math_Expression_Input', index=2),
        'found_func': found_text_func('MATH EXPRESSION INPUT')
    },
    'Problem LaTex': {
        'steps': step_selector_list('problem', 'Problem_Written_in_LaTeX', index=2),
        'found_func': found_text_func('PROBLEM WRITTEN IN LATEX')
    },
    'Adaptive Hint': {
        'steps': step_selector_list('problem', 'Problem_with_Adaptive_Hint', index=2),
        'found_func': found_text_func('PROBLEM WITH ADAPTIVE HINT')
    },
}
