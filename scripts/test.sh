result=$(mysql -u azkaban -pazkaban azkaban -se "select * FROM executors where active=1;")
echo ${result}
