package "nginx"

user "www-data" do
  system true
  shell "/bin/false"
  home "/var/www"
end

directory "/var/log/nginx" do
  mode 0755
  owner "www-data"
  action :create
end

directory "/etc/nginx/sites-enabled" do
  mode 0755
  owner "root"
  action :create
end

cookbook_file "/etc/nginx/mime.types" do
  source "mime.types"
  owner "root"
  group "root"
  mode 0644
  notifies :reload, "service[nginx]"
end

cookbook_file "/etc/nginx/nginx.conf" do
  source "nginx.conf"
  owner "root"
  group "root"
  mode 0644
  notifies :reload, "service[nginx]"
end

cookbook_file "/etc/nginx/sites-enabled/default" do
  source "default.conf"
  owner "root"
  group "root"
  mode 0644
  notifies :reload, "service[nginx]"
end

service "nginx" do
  action [:enable, :start]
  supports :status => true, :restart => true, :reload => true
end
