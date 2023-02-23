from bs4 import BeautifulSoup
import requests
import random


class ScrapeCompany:
    def __init__(self, url):
        self.url = url
        user_agent = None
        random_line = random.randint(0, 55)
        with open('storage/user_agents.txt', 'r') as f:
            for i, line in enumerate(f):
                if i == random_line:
                    user_agent = line.strip()
                    break

        try:
            self.soup = BeautifulSoup(requests.get(url, headers={
                'User-Agent': user_agent
            }).text, 'html.parser')
        except Exception as e:
            print(f"Cannot get {url}: {e}")

    def scrape(self):
        if "500" in self.soup.title.text:
            return 500

        basic_info = self.get_basic_info()
        details = self.get_details()
        main_staff = self.get_main_staff()
        shareholders = self.get_shareholders()
        branches = self.get_branches()
        changes = self.get_changes()
        foreign_investments = self.get_foreign_investments()
        annual_reports = self.get_annual_reports()

        return {
            'basic_info': basic_info,
            'details': details,
            'main_staff': main_staff,
            'shareholders': shareholders,
            'branches': branches,
            'changes': changes,
            'foreign_investments': foreign_investments,
            'annual_reports': annual_reports,
        }

    def get_basic_info(self):
        uuid = self.url.split('/')[-1]
        title = self.soup.select_one('.detail-banner-title p').text.strip()
        phone = self.soup.select_one(
            '.detail-banner-phone').text.strip().split('：')[1].strip()
        email = self.soup.select_one(
            '.detail-banner-email').text.strip().split('：')[1].strip()
        website = self.soup.select_one('.detail-banner-li.website a')
        if website:
            website = website.text.strip()
        else:
            website = "-"

        return {
            'uuid': uuid,
            'title': title,
            'phone': phone != "-" and phone or None,
            'email': email != "-" and email or None,
            'website': website != "-" and website or None,
        }

    def get_details(self):
        data = {}
        details_table = self.soup.select('table.business tr')
        for details in details_table:
            count_of_cells = len(details.select('td'))
            if count_of_cells == 2:
                key = details.select_one('td:nth-of-type(1)').text.strip()
                data[key] = details.select_one(
                    'td:nth-of-type(2)').text.strip()
            elif count_of_cells == 4:
                key = details.select_one('td:nth-of-type(1)').text.strip()
                data[key] = details.select_one(
                    'td:nth-of-type(2)').text.strip()
                key = details.select_one('td:nth-of-type(3)').text.strip()
                data[key] = details.select_one(
                    'td:nth-of-type(4)').text.strip()

        return data

    def get_main_staff(self):
        main_staff = []
        staff_table = self.soup.select('table.main-staff tr')
        for staff in staff_table:
            count_of_cells = len(staff.select('td'))
            if count_of_cells == 2:
                name = staff.select_one('td:nth-of-type(1)').text.strip()
                position = staff.select_one('td:nth-of-type(2)').text.strip()
                try:
                    main_staff.append({
                        'name': name.split('\n\n')[1].strip(),
                        'position': position,
                    })
                except:
                    pass

        return main_staff

    def get_branches(self):
        branches = []
        branches_table = self.soup.select('.branch-info table.shareholder tr')
        for branch in branches_table:
            count_of_cells = len(branch.select('td'))
            if count_of_cells == 4:
                name = branch.select_one('td:nth-of-type(1) p').text.strip()
                person = branch.select_one('td:nth-of-type(2)').text.strip()
                date = branch.select_one('td:nth-of-type(3)').text.strip()
                status = branch.select_one('td:nth-of-type(4)').text.strip()

                branches.append({
                    'name': name,
                    'person': person,
                    'date': date,
                    'status': status,
                })

        return branches

    def get_foreign_investments(self):
        foreign_investments = []
        foreign_investments_table = self.soup.select(
            '.foreign table.connection tr')
        for foreign_investment in foreign_investments_table:
            count_of_cells = len(foreign_investment.select('td'))
            if count_of_cells == 6:
                name = foreign_investment.select_one(
                    'td:nth-of-type(1) p').text.strip()
                person = foreign_investment.select_one(
                    'td:nth-of-type(2)').text.strip()
                registered_capital = foreign_investment.select_one(
                    'td:nth-of-type(3)').text.strip()
                ratio = foreign_investment.select_one(
                    'td:nth-of-type(4)').text.strip()
                date = foreign_investment.select_one(
                    'td:nth-of-type(5)').text.strip()
                status = foreign_investment.select_one(
                    'td:nth-of-type(6)').text.strip()

                foreign_investments.append({
                    'name': name,
                    'person': person,
                    'registered_capital': registered_capital,
                    'ratio': ratio,
                    'date': date,
                    'status': status,
                })

        return foreign_investments

    def get_annual_reports(self):
        data = {}
        reports = self.soup.select('.year-report a')
        for report in reports:
            response = requests.get(report['href'])
            search = "哎呀，您的页面好像消失了~"
            if search in response.text:
                continue

            soup = BeautifulSoup(response.text, 'html.parser')
            year = soup.select_one('.all-report a.active')
            if year is None:
                continue

            year = year.text.split(' ')[0].strip()

            report_data = {}
            basic_info = soup.select('.report-left table:nth-of-type(1) tr')
            for info in basic_info:
                count_of_cells = len(info.select('td'))
                if count_of_cells == 2:
                    key = info.select_one('td:nth-of-type(1)').text.strip()
                    value = info.select_one('td:nth-of-type(2)').text.strip()
                    report_data[key] = value

                if count_of_cells == 4:
                    key = info.select_one('td:nth-of-type(1)').text.strip()
                    value = info.select_one('td:nth-of-type(2)').text.strip()
                    report_data[key] = value
                    key = info.select_one('td:nth-of-type(3)').text.strip()
                    value = info.select_one('td:nth-of-type(4)').text.strip()
                    report_data[key] = value

            assets = soup.select('.report-left table:nth-of-type(2) tr')
            for asset in assets:
                count_of_cells = len(asset.select('td'))
                if count_of_cells == 2:
                    key = asset.select_one('td:nth-of-type(1)').text.strip()
                    value = asset.select_one('td:nth-of-type(2)').text.strip()
                    report_data[key] = value

                if count_of_cells == 4:
                    key = asset.select_one('td:nth-of-type(1)').text.strip()
                    value = asset.select_one('td:nth-of-type(2)').text.strip()
                    report_data[key] = value
                    key = asset.select_one('td:nth-of-type(3)').text.strip()
                    value = asset.select_one('td:nth-of-type(4)').text.strip()
                    report_data[key] = value

            report_data['report_url'] = report['href']
            data[year] = report_data

        return data

    def get_shareholders(self):
        shareholders = []
        shareholders_table = self.soup.select(
            '.shareholder-info table.shareholder tr')
        for shareholder in shareholders_table:
            count_of_cells = len(shareholder.select('td'))
            if count_of_cells == 4:
                name = shareholder.select_one(
                    'td:nth-of-type(1) p').text.strip()
                ratio = shareholder.select_one(
                    'td:nth-of-type(2)').text.strip()
                capital = shareholder.select_one(
                    'td:nth-of-type(3)').text.strip()
                date = shareholder.select_one('td:nth-of-type(4)').text.strip()

                shareholders.append({
                    'name': name,
                    'ratio': ratio,
                    'capital': capital,
                    'date': date,
                })

        return shareholders

    def get_changes(self):
        changes = []
        changes_table = self.soup.select('table.change-log tr')
        for change in changes_table:
            count_of_cells = len(change.select('td'))
            if count_of_cells == 4:
                date = change.select_one('td:nth-of-type(1)').text.strip()
                change_type = change.select_one(
                    'td:nth-of-type(2)').text.strip()
                before = change.select_one('td:nth-of-type(3)').text.strip()
                after = change.select_one('td:nth-of-type(4)').text.strip()

                changes.append({
                    'date': date,
                    'change_type': change_type,
                    'before': before,
                    'after': after,
                })

        return changes