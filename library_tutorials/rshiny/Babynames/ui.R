
# Dashboard Page Has three parts, a header, sidebar and body
ui <- dashboardPage(skin='black',
                    dashboardHeader(title='Babynames Dataset'),
                    dashboardSidebar(
                      sidebarMenu(
                        menuItem("Name Analysis", tabName = "tab1", icon = icon("dashboard")),
                        menuItem("Both Male/Female name analysis", tabName = "tab2", icon = icon("dashboard")),
                        menuItem("Name Comparison / Regular expression search", tabName = "tab3", icon = icon("dashboard")),
                        menuItem("Year Rank charts / Rank Analysis", tabName = "tab4", icon = icon("dashboard"))
                      )
                    ),
                    dashboardBody(
                      tabItems(
                        # First tab content
                        tabItem(tabName = "tab1", mod_name_analysis('id-nameAnalysis1')
),
                        tabItem(tabName = 'tab2', box(title = "Box Title", width = NULL, background = "green", "Tab 1 Text"))
                      )
                    )
)