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

    def parse(self, response):

        divs_data = response.xpath(
            '//*[@id="ContentPlaceHolder1_UpdatePanel1"]/div'
        )
        # div_pagination = response.xpath(
        # '//*[@id="ContentPlaceHolder1_dpNoticia"]'
        # )
        clean_divs_data = self.clean_list(divs_data)

        for div in clean_divs_data:
            temp_info = div.xpath('./text()').extract()

            info = self.clean_line(temp_info)

            yield {
                'registro': info
            }
