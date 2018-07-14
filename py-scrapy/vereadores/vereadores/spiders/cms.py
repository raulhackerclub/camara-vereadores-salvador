# -*- coding: utf-8 -*-
import scrapy


class CmsSpider(scrapy.Spider):
    name = 'cms'
    start_urls = ['http://www.cms.ba.gov.br/despesa.aspx/']

    @staticmethod
    def clean_list(list):
        # remove trash of list
        del list[:2]
        del list[-1]

        return list

    @staticmethod
    def clean_line(line):
        return line[1::2]

    @staticmethod
    def has_next(div_pagination, actual_page):
        dp = div_pagination.xpath('./a/text()').extract()
        position = dp.index(str(actual_page))
        if dp[position+1] != '>':
            return True
        else:
            return False

    def parse(self, response):
        div_pagination = response.xpath(
            '//*[@id="ContentPlaceHolder1_dpNoticia"]'
        )

        view_state = response.xpath('//*[@id="__VIEWSTATE"]').extract_first()
        event_validation = response.xpath(
            '//*[@id="__EVENTVALIDATION"]'
        ).extract_first()
        actual_page = int(div_pagination.xpath(
            './span/text()'
        ).extract_first()) + 1

        while self.has_next(div_pagination, actual_page):

            yield scrapy.Request(
                url="http://www.cms.ba.gov.br/despesa.aspx/",
                callback=self.parse_detail,
                method='POST',
                headers={
                    'pagina': actual_page,
                    'viewState': view_state,
                    'eventValidation': event_validation,
                    '__EVENTTARGET':
                        'ctl00$ContentPlaceHolder1$dpNoticia$ctl01$ctl%s'
                        % (actual_page + 1),
                        'ctl00$ContentPlaceHolder1$ToolkitScriptManager1':
                        'ctl00$ContentPlaceHolder1$UpdatePanel1|ctl00$ContentPlaceHolder1$dpNoticia$ctl01$ctl%s'
                        % (actual_page + 1)
                }
            )

    def parse_detail(self, response):
        divs_data = response.xpath(
            '//*[@id="ContentPlaceHolder1_UpdatePanel1"]/div'
        )

        clean_divs_data = self.clean_list(divs_data)

        for div in clean_divs_data:
            temp_info = div.xpath('./text()').extract()

            info = self.clean_line(temp_info)

            yield {
                'registro': info
            }
