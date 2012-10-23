group "#{node[:project][:group]}"

user "#{node[:project][:user]}" do
  gid "#{node[:project][:group]}"
  home "/home/#{node[:project][:user]}"
  shell "/bin/bash"
end


directory "/home/#{node[:project][:user]}/.ssh" do
  owner "#{node[:project][:user]}"
  group "#{node[:project][:group]}"
  mode 0700
  recursive true
end

execute "echo 'export DJANGO_ENVIRON=#{node[:project][:environment]}' >> /home/#{node[:project][:user]}/.profile" do
  user "#{node[:project][:user]}"
  group "#{node[:project][:group]}"
  not_if "cat /home/#{node[:project][:user]}/.profile | grep 'export DJANGO_ENVIRON=#{node[:project][:environment]}'"
end


service "postgresql" do
 action :start
end

bash "setup-pg-user" do
  user "postgres"
  code <<-EOH
  psql -c '\\du' | grep -q '#{node[:project][:db_user]}'
  if test "$(echo $?)" != "0"; then
    createuser -S -d -R -w #{node[:project][:db_user]};
  fi
  EOH
end

bash "setup-pg-db" do
  user "postgres"
  code <<-EOH
  psql -l | grep '#{node[:project][:db_user]}' | grep -q '#{node[:project][:db]}';
  if test "$(echo $?)" != "0"; then
     createdb -O #{node[:project][:db_user]} -w #{node[:project][:db]};
  fi
  EOH
end


directory "#{node[:project][:db_backup_root]}" do
  owner "postgres"
  group "postgres"
  mode 0700
  recursive true
end
