#
# Author:: Seth Chisamore <schisamo@opscode.com>
# Cookbook Name:: python
# Recipe:: package
#
# Copyright 2011, Opscode, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

python_pkgs = value_for_platform(
  ["debian","ubuntu"] => {
    "default" => ["python","python-dev"]
  },
  ["centos","redhat","amazon", "fedora"] => {
    "default" => ["python26","python26-devel"]
  },
  ["freebsd"] => {
    "default" => ["python"]
  },
  "default" => ["python","python-dev"]
)

python_pkgs.each do |pkg|
  package pkg do
    action :install
  end
end

