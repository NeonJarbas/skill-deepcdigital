#!/usr/bin/env python3
from setuptools import setup

# skill_id=package_name:SkillClass
PLUGIN_ENTRY_POINT = 'skill-deepcdigital.jarbasai=skill_deepcdigital:DeepCDigitalSkill'

setup(
    # this is the package name that goes on pip
    name='ovos-skill-deepcdigital',
    version='0.0.1',
    description='ovos Full Free Films skill plugin',
    url='https://github.com/JarbasSkills/skill-deepcdigital',
    author='JarbasAi',
    author_email='jarbasai@mailfence.com',
    license='Apache-2.0',
    package_dir={"skill_deepcdigital": ""},
    package_data={'skill_deepcdigital': ['locale/*', 'ui/*']},
    packages=['skill_deepcdigital'],
    include_package_data=True,
    install_requires=["ovos_workshop~=0.0.5a1"],
    keywords='ovos skill plugin',
    entry_points={'ovos.plugin.skill': PLUGIN_ENTRY_POINT}
)
