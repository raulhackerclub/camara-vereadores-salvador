# 1st, launch the Selenium server. 
# Dependencies: java
# Run '$java -jar selenium-server-standalone-x.xx.x.jar

require(RSelenium)

remDr <- remoteDriver(remoteServerAddr = "localhost" 
                      , port = 4444
                      , browserName = "firefox")
remDr$open()
remDr$navigate("http://www.cms.ba.gov.br/despesa.aspx")

# Temos que replicar as requests para mudar de página no site.
# O código é 
# As tentativas abaixo não funcionaram, mas ilustram a sintaxe do R
# RSelenium
# https://ropensci.org/tutorials/rselenium_tutorial/

webElem<-remDr$findElement(using = 'css selector', 
                           value = "javascript:__ctl00$ContentPlaceHolder1$dpNoticia$ctl01$ctl02")

script <- "__doPostBack('ctl00$ContentPlaceHolder1$dpNoticia$ctl01$ctl02','')"

remDr$executeScript(script, args = list())
remDr$executeScript("arguments[0].click();"
                    , list(remDr$findElement("id", "javascript:__ctl00$ContentPlaceHolder1$dpNoticia$ctl01$ctl02")))

