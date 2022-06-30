// Copyright (C) 2021 Bosutech XXI S.L.
//
// nucliadb is offered under the AGPL v3.0 and as commercial software.
// For commercial licensing, contact us at info@nuclia.com.
//
// AGPL:
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as
// published by the Free Software Foundation, either version 3 of the
// License, or (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
// GNU Affero General Public License for more details.
//
// You should have received a copy of the GNU Affero General Public License
// along with this program. If not, see <http://www.gnu.org/licenses/>.
//

use std::io::Cursor;

use nucliadb_protos::*;
use nucliadb_service_interface::prelude::*;
use nucliadb_service_interface::vectos_interface::VectorServiceConfiguration;
use nucliadb_vectors::service::VectorWriterService;
use prost::Message;
use tempdir::TempDir;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let dir = TempDir::new("payload_dir").unwrap();
    let vsc = VectorServiceConfiguration {
        no_results: None,
        path: dir.path().to_str().unwrap().to_string(),
    };
    let mut writer = VectorWriterService::start(&vsc).await.unwrap();
    let payload_dir = std::path::Path::new("Path_to_data");
    assert!(payload_dir.exists());
    for file_path in std::fs::read_dir(&payload_dir).unwrap() {
        let file_path = file_path.unwrap().path();
        println!("processing {file_path:?}");
        let content = std::fs::read(&file_path).unwrap();
        let resource = Resource::decode(&mut Cursor::new(content)).unwrap();
        println!("Adding resource {}", file_path.display());
        let res = writer.set_resource(&resource);
        assert!(res.is_ok());
        println!("Resource added");
    }
    Ok(())
}
