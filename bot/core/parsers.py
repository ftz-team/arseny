from typing import Iterable
import requests
import math
from string import Template
from bs4 import BeautifulSoup
import requests


def get_latest_from_vk(n : int) -> Iterable:
    pages = math.ceil(n / 20)
    ans_tmp = []
    ans = []
    for i in range(pages):
        r = requests.get("https://api.iconjob.co/api/web/v1/jobs?sort=fresh&page="+str(i)+"&per_page=20")
        ans_tmp.extend(r.json()['jobs'])
    for i in ans_tmp:
        if len(i['professions'])>0:
            ans.append({
                'custom_position' :i['professions'][0]['title'][:1].title() + i['professions'][0]['title'][1:],
                'description' : i['description'],
                'salary_from' : i['salary_from'],
                'salary_to' : i['salary_to'],
                'link' : "https://vkrabota.ru/vacancy/"+i['hashid'],
            })
        else:
            ans.append({
                'custom_position' :  i['title'],
                'description' : i['description'],
                'salary_from' : i['salary_from'],
                'salary_to' : i['salary_to'],
                'link' : "https://vkrabota.ru/vacancy/"+i['hashid'],
            })
    return ans


import re
CLEANR = re.compile('<.*?>') 

def cleanhtml(raw_html):
  cleantext = re.sub(CLEANR, '', raw_html)
  return cleantext

def getLatestFromTrud(n : int) -> Iterable:
    pages = math.ceil(n / 10)
    ans_tmp = []
    ans = []
    for i in range(pages):
        r = requests.get("https://trudvsem.ru/iblocks/_catalog/flat_filter_prr_search_vacancies/data?filter=%7B%22regionCode%22%3A%5B%225000000000000%22%5D%2C%22publishDateTime%22%3A%5B%22EXP_MAX%22%5D%7D&orderColumn=PUBLISH_DATE_DESC&page="+str(i)+"&pageSize=10")
        rjson = r.json()
        ans_tmp.extend([(x[0],x[2]) for x in rjson['result']['data']])
        

    for i in ans_tmp:
        r = requests.get('https://trudvsem.ru/iblocks/job_card?companyId='+i[-1]+'&vacancyId='+i[0])
        vacancy = r.json()['data']['vacancy']
        ans.append({
            'custom_position' : vacancy['vacancyName'],
            'description' : cleanhtml(vacancy.get('additionalRequirements','')) + cleanhtml(vacancy.get('positionResponsibilities', '')),
            'salary_from' : vacancy.get('salaryMin', 18000),
            'salary_to' : vacancy.get('salaryMax', 18000),
            'link' : 'https://trudvsem.ru/vacancy/card/'+i[-1]+'/'+i[0],
        })
    return ans



url_tmpl = Template(
    "https://www.rabota.ru/vacancy/?sort=date&page=$page")


def get_last_vacancies_from_rabota_ru(n: int):
	res = []
	page = 1

	while len(res) < n:
		for i in __parse_page(page, len(res), n):
			res.append(i)
		page += 1

	if len(res) > n:
		res = res[:len(res-n)]

	return res


def __parse_page(page: int, cur_n: int, n: int) -> list:
	url = url_tmpl.substitute(page=page)
	rp = requests.get(url)
	soup = BeautifulSoup(rp.content, 'html.parser')

	res = []
	
	for div in soup.find_all('div', class_='vacancy-preview-card__wrapper'):
		if cur_n >= n:
			return res
		url = __get_vac_url(div)
		if not url:
			continue
		vac = __get_vac_from_url(url)
		res.append(vac)
		cur_n += 1

	return res


def __get_vac_url(div):
	try:
		return div.find('h3', class_='vacancy-preview-card__title').find('a')['href'].strip()
	except:
		return ''


def __get_vac_from_url(url: str):
	full_url = 'https://rabota.ru' + url
	rp = requests.get(full_url)
	# print(rp.status_code)
	soup = BeautifulSoup(rp.content, 'html.parser')

	title = (soup.find('h1', class_='vacancy-card__title') or \
		soup.find('div', class_='branding-vacancy-card-header__title')).text.strip()
	#print(title)
	
	salary = (soup.find('h3', class_='vacancy-card__salary') or \
		soup.find('div', class_='branding-vacancy-card-header__salary')).text.strip()
	
	info = (', '.join([' '.join(x.text.split()) for x in soup.find_all('div', class_='info-table__text')]) or \
		soup.find('span', class_='vacancy-requirements_uppercase').text.strip()).split(', ')
	schedule, experience, education = info[0], __parse_experience(info[1]), __parse_education(info[2])
	#print(schedule, experience, education)

	salary = (soup.find('h3', class_='vacancy-card__salary') or \
		soup.find('div', class_='branding-vacancy-card-header__salary')).text.strip()
	salary_from, salary_to = __parse_salary(salary)
	#print(salary_from, salary_to)

	desc = (soup.find('div', class_='description') or \
		soup.find('div', class_='vacancy-card__description')).text.strip()
	desc = desc[:desc.find('Адрес\n')]

	return {
		'custom_position': title,
		'operating_schedule': schedule,
		'salary_from': salary_from,
		'salary_to': salary_to,
		'description': desc,
		'offer_education': education,
		'offer_experience_year_count': experience,
		'link': full_url,
	}


def __parse_salary(s: str):
	s_from = None
	s_to = None
	if 'от ' in s:
		s_from = __get_num_from_str(s)
	elif 'до ' in s:
		s_to = __get_num_from_str(s)
	elif '—' in s:
		s_from = __get_num_from_str(s.split('—')[0])
		s_to = __get_num_from_str(s.split('—')[1])

	return s_from, s_to


def __parse_experience(s: str):
	exp = None
	if 'от ' in s.lower():
		exp = __get_num_from_str(s)

	return exp


def __parse_education(s: str):
	return s.replace('образование', '').strip()


def __get_num_from_str(txt: str) -> int:
	return int(''.join([s for s in txt.split() if s.isdigit()]))